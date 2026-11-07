"""Reset safety contracts, exclusively against committed disposable fixtures."""

import os
from pathlib import Path
import queue
import re
import shutil
import stat
import subprocess
import threading
import time
import unittest

from active_fixture import exercise_path, solve
from test_branch_policy import BranchFixture


class ResetCliTests(BranchFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.git("switch", "-c", "practice/reset")
        self.baseline = self.answer().read_bytes()
        self.main_oid = self.git("rev-parse", "refs/heads/main")

    def reset(self, *, input="yes\n", code=0, selection="python/hello"):
        return self.cli("reset", selection, input=input, code=code)

    def assert_no_backups(self):
        self.assertFalse((self.root / ".polyglot").exists())

    def assert_backup(self, output, expected):
        match = re.search(r"Backup: ([^\r\n]+)", output)
        self.assertIsNotNone(match, output)
        backup = Path(match[1])
        self.assertTrue(backup.is_absolute())
        self.assertTrue(backup.is_relative_to(self.root / ".polyglot"))
        self.assertEqual(backup.read_bytes(), expected)
        return backup

    def test_reset_only_selected_file_preserves_exact_backup_and_git(self):
        learner = b"# learner bytes\r\n\r\n\x00\xff\n\n"
        self.answer().write_bytes(learner)
        solve(self.root, "python", "find_in_string")
        sources, metadata = self.sources(), self.git_files()
        output = self.reset()
        self.assertIn(f"Reset baseline: refs/heads/main at {self.main_oid}", output)
        self.assertIn("Reset python/hello? [y/N]:", output)
        self.assertIn("Reset: python/hello", output)
        backup = self.assert_backup(output, learner)
        self.assertEqual(self.answer().read_bytes(), self.baseline)
        for relative, content in sources.items():
            if relative != str(self.answer().relative_to(self.root)):
                path = self.root / relative
                self.assertEqual(path.read_bytes() if path.is_file() else None, content)
        self.assertEqual(self.git_files(), metadata)
        self.assertNotEqual(backup, self.answer())

    def test_main_blob_not_committed_learner_head_is_baseline(self):
        self.git("switch", "main")
        self.baseline += b"\n\n\n"
        self.answer().write_bytes(self.baseline)
        self.git("add", "practice/python/exercises/hello.py")
        self.commit()
        self.git("switch", "practice/reset")
        solve(self.root, "python", "hello")
        self.git("add", "practice/python/exercises/hello.py")
        self.commit()
        learner = self.answer().read_bytes()
        output = self.reset(input="y\n")
        self.assert_backup(output, learner)
        self.assertEqual(self.answer().read_bytes(), self.baseline)

    @unittest.skipUnless(os.name == "posix", "requires inode and Unix permission checks")
    def test_normal_reset_retains_original_inode_in_private_recovery(self):
        solve(self.root, "python", "hello")
        original = self.answer().stat()
        learner = self.answer().read_bytes()
        output = self.reset()
        match = re.search(r"Recovery: ([^\r\n]+)", output)
        self.assertIsNotNone(match, output)
        recovery = Path(match[1])
        self.assertEqual(recovery.read_bytes(), learner)
        self.assertEqual(recovery.stat().st_ino, original.st_ino)
        self.assertEqual(recovery.stat().st_dev, original.st_dev)
        self.assertEqual(recovery.stat().st_mode & 0o777, 0o600)
        self.assertNotEqual(self.answer().stat().st_ino, original.st_ino)

    def test_same_named_tag_cannot_override_full_main_ref(self):
        solve(self.root, "python", "hello")
        self.git("add", ".")
        self.commit()
        self.git("tag", "main")
        self.reset()
        self.assertEqual(self.answer().read_bytes(), self.baseline)

    def assert_reset_ignores_replacement(self, object_type):
        relative = "practice/python/exercises/hello.py"
        solve(self.root, "python", "hello")
        learner = self.answer().read_bytes()
        self.git("add", relative)
        self.commit()
        learner_oid = self.git("rev-parse", "HEAD")
        if object_type == "commit":
            original, replacement = self.main_oid, learner_oid
        else:
            original = self.git("--no-replace-objects", "rev-parse", f"{self.main_oid}:{relative}")
            replacement = self.git("--no-replace-objects", "rev-parse", f"{learner_oid}:{relative}")
        self.git("replace", original, replacement)
        self.assertEqual(self.git("show", f"{self.main_oid}:{relative}"), learner.decode().strip())
        expected = subprocess.run(
            ["git", "--no-optional-locks", "--no-replace-objects", "show",
             f"{self.main_oid}:{relative}"],
            cwd=self.root, env=self.env, capture_output=True, timeout=30,
        )
        self.assertEqual(expected.returncode, 0, expected.stderr)
        self.assertEqual(expected.stdout, self.baseline)
        self.assertNotEqual(expected.stdout, learner)
        metadata = self.git_files()
        output = self.reset()
        self.assertIn(f"Reset baseline: refs/heads/main at {self.main_oid}", output)
        self.assertEqual(self.git_files(), metadata)
        self.assertEqual(self.answer().read_bytes(), expected.stdout)
        self.assertIn("Reset: python/hello", output)
        self.assert_backup(output, learner)

    def test_commit_replacement_cannot_substitute_main_baseline(self):
        self.assert_reset_ignores_replacement("commit")

    def test_blob_replacement_cannot_substitute_main_baseline(self):
        self.assert_reset_ignores_replacement("blob")

    @unittest.skipUnless(os.name == "posix", "requires Unix modes and subprocess umask")
    def test_reset_keeps_backup_and_source_private_under_permissive_umask(self):
        solve(self.root, "python", "hello")
        learner = self.answer().read_bytes()
        self.answer().chmod(0o600)
        metadata = self.git_files()
        with subprocess.Popen(
            self.command("reset", "python/hello"), cwd=self.base, env=self.env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, umask=0o022,
        ) as process:
            stdout, stderr = process.communicate("yes\n", timeout=45)
            self.assertEqual(process.returncode, 0, stdout + stderr)
        backup = self.assert_backup(stdout + stderr, learner)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.answer().stat().st_mode), 0o600)
        self.assertEqual(self.answer().read_bytes(), self.baseline)
        self.assertEqual(self.git_files(), metadata)

    def test_pristine_is_success_without_prompt_or_backup(self):
        before, metadata = self.sources(), self.git_files()
        output = self.reset(input="")
        self.assertNotIn("[y/N]", output)
        self.assert_no_backups()
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_empty_no_and_eof_cancel_without_any_writes(self):
        solve(self.root, "python", "hello")
        before, metadata = self.sources(), self.git_files()
        for response in ("\n", "no\n", "n\n", "", "YES please\n"):
            with self.subTest(response=response):
                output = self.reset(input=response)
                self.assertIn("Reset cancelled", output)
                self.assert_no_backups()
                self.assertEqual(self.sources(), before)
                self.assertEqual(self.git_files(), metadata)

    def test_main_is_blocked(self):
        self.git("switch", "main")
        self.assert_blocked("reset", "python/hello")
        self.assert_no_backups()

    def test_detached_is_blocked(self):
        self.git("switch", "--detach")
        self.assert_blocked("reset", "python/hello")

    def test_nonrepository_is_blocked(self):
        shutil.rmtree(self.root / ".git")
        self.assert_blocked("reset", "python/hello")

    def test_missing_main_is_blocked(self):
        self.git("branch", "-D", "main")
        solve(self.root, "python", "hello")
        self.assert_blocked("reset", "python/hello")
        self.assert_no_backups()

    def test_path_absent_from_main_has_no_starter_or_head_fallback(self):
        self.git("switch", "main")
        self.git("rm", "practice/python/exercises/hello.py")
        self.commit()
        self.git("switch", "practice/reset")
        solve(self.root, "python", "hello")
        self.assert_blocked("reset", "python/hello")
        self.assert_no_backups()

    def test_uncommitted_new_exercise_has_no_baseline(self):
        self.git("switch", "main")
        self.git("rm", "practice/python/exercises/hello.py")
        self.commit()
        self.git("switch", "-c", "practice/new-exercise")
        solve(self.root, "python", "hello")
        self.assert_blocked("reset", "python/hello")
        self.assert_no_backups()

    def test_missing_working_file_is_restored_from_main(self):
        self.answer().unlink()
        metadata = self.git_files()
        output = self.reset()
        self.assertEqual(self.answer().read_bytes(), self.baseline)
        self.assertNotIn("Backup:", output)
        self.assertEqual(self.git_files(), metadata)

    def test_staged_content_is_retained_exactly(self):
        solve(self.root, "python", "hello")
        self.git("add", "practice/python/exercises/hello.py")
        self.answer().write_bytes(b"# unstaged learner edit\n\n")
        metadata = self.git_files()
        staged = self.git("show", ":practice/python/exercises/hello.py")
        self.assert_backup(self.reset(), b"# unstaged learner edit\n\n")
        self.assertEqual(self.git("show", ":practice/python/exercises/hello.py"), staged)
        self.assertEqual(self.git_files(), metadata)
        self.assertEqual(self.answer().read_bytes(), self.baseline)

    def test_target_symlink_and_directory_are_refused(self):
        outside = self.base / "outside learner file"
        outside.write_bytes(b"outside must survive\n")
        self.answer().unlink()
        self.answer().symlink_to(outside)
        self.assert_blocked("reset", "python/hello")
        self.assertEqual(outside.read_bytes(), b"outside must survive\n")
        self.assert_no_backups()
        self.answer().unlink()
        self.answer().mkdir()
        self.assert_blocked("reset", "python/hello")
        self.assert_no_backups()

    def test_canonical_main_symlink_mode_is_refused(self):
        self.git("switch", "main")
        self.answer().unlink()
        self.answer().symlink_to("../README.md")
        self.git("add", "practice/python/exercises/hello.py")
        self.commit()
        self.git("switch", "-c", "practice/symlink-baseline")
        self.answer().unlink()
        solve(self.root, "python", "hello")
        self.assert_blocked("reset", "python/hello")
        self.assert_no_backups()

    def test_backup_directory_symlinks_never_write_outside(self):
        solve(self.root, "python", "hello")
        outside = self.base / "outside backups"
        outside.mkdir()
        (outside / "sentinel").write_bytes(b"untouched\n")
        for relative in (".polyglot", ".polyglot/backups"):
            with self.subTest(relative=relative):
                link = self.root / relative
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(outside, target_is_directory=True)
                before = self.answer().read_bytes()
                self.reset(code=2)
                self.assertEqual(self.answer().read_bytes(), before)
                self.assertEqual(list(outside.iterdir()), [outside / "sentinel"])
                self.assertEqual((outside / "sentinel").read_bytes(), b"untouched\n")
                link.unlink()
        shutil.rmtree(self.root / ".polyglot")

    def test_backup_failure_preserves_original(self):
        solve(self.root, "python", "hello")
        original = self.answer().read_bytes()
        (self.root / ".polyglot").write_bytes(b"not a directory\n")
        metadata = self.git_files()
        self.reset(code=2)
        self.assertEqual(self.answer().read_bytes(), original)
        self.assertEqual((self.root / ".polyglot").read_bytes(), b"not a directory\n")
        self.assertEqual(self.git_files(), metadata)

    def test_legacy_ignored_answers_never_imported_modified_or_deleted(self):
        for language, filename in (("python", "answers.py"), ("rust", "answers.rs")):
            legacy = self.root / "practice" / language / filename
            legacy.write_bytes(b"invalid legacy source\x00\xff\r\n\n")
        legacy_before = {p: p.read_bytes() for p in
                         (self.root / "practice/python/answers.py", self.root / "practice/rust/answers.rs")}
        self.cli("check", "python/hello", code=1)
        self.cli("start", "python/hello")
        self.cli("practice", "python/hello", input="q\n")
        solve(self.root, "python", "hello")
        self.reset()
        for path, content in legacy_before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_reset_argument_shapes_are_strict(self):
        before, metadata = self.sources(), self.git_files()
        for args in ((), ("python",), ("all",), ("python/hello", "--yes"),
                     ("--yes", "python/hello"), ("python/hello", "extra")):
            with self.subTest(args=args):
                self.cli("reset", *args, code=2)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_rust_reset_uses_its_own_main_blob(self):
        path = exercise_path(self.root, "rust")
        baseline = path.read_bytes()
        solve(self.root, "rust")
        learner = path.read_bytes()
        output = self.reset(selection="rust/hello")
        self.assert_backup(output, learner)
        self.assertEqual(path.read_bytes(), baseline)

    def test_new_python_resets_use_main_blob_and_preserve_siblings(self):
        baselines = {name: exercise_path(self.root, "python", name).read_bytes()
                     for name in ("binary_search", "fibonacci")}
        for name in ("binary_search", "fibonacci"):
            with self.subTest(name=name):
                path = exercise_path(self.root, "python", name)
                baseline = baselines[name]
                solve(self.root, "python")
                learner = path.read_bytes()
                before, metadata = self.sources(), self.git_files()
                output = self.reset(selection="python/" + name)
                self.assert_backup(output, learner)
                self.assertEqual(path.read_bytes(), baseline)
                for relative, content in before.items():
                    if relative != str(path.relative_to(self.root)):
                        source = self.root / relative
                        self.assertEqual(source.read_bytes() if source.is_file() else None, content)
                self.assertEqual(self.git_files(), metadata)

    def test_new_rust_resets_preserve_staged_index_and_all_siblings(self):
        names = ("find_in_string", "length_of_last_word", "binary_search", "fibonacci")
        baselines = {name: exercise_path(self.root, "rust", name).read_bytes() for name in names}
        for name in names:
            with self.subTest(name=name):
                solve(self.root, "rust")
                path = exercise_path(self.root, "rust", name)
                relative = str(path.relative_to(self.root))
                self.git("add", relative)
                path.write_bytes(path.read_bytes() + b"\n// unstaged learner bytes\r\n")
                learner = path.read_bytes()
                before, metadata = self.sources(), self.git_files()
                output = self.reset(selection="rust/" + name)
                self.assert_backup(output, learner)
                self.assertEqual(path.read_bytes(), baselines[name])
                self.assertEqual(self.git_files(), metadata)
                for sibling, content in before.items():
                    if sibling != relative:
                        source = self.root / sibling
                        self.assertEqual(source.read_bytes() if source.is_file() else None, content)

    def test_session_reset_aliases_stay_selected_and_next_rechecks(self):
        for alias in ("reset", "r"):
            with self.subTest(alias=alias):
                solve(self.root, "python", "hello")
                output = self.cli("practice", "python/hello",
                                  input=f"check\n{alias}\nyes\nnext\nprompt\nq\n")
                self.assertIn("Passed", output)
                self.assertIn("Reset: python/hello", output)
                self.assertIn("Attempt failed", output)
                self.assertNotIn("Exercise: python/find_in_string", output)
                self.assertEqual(self.answer().read_bytes(), self.baseline)

    def test_session_confirmation_eof_cancels_and_exits_cleanly(self):
        solve(self.root, "python", "hello")
        before, metadata = self.sources(), self.git_files()
        output = self.cli("practice", "python/hello", input="reset\n")
        self.assertIn("Reset cancelled", output)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)
        self.assert_no_backups()

    def live_reset(self, mutate):
        """Read characters because the confirmation prompt has no newline."""
        process = subprocess.Popen(self.command("reset", "python/hello"), cwd=self.base,
                                   env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, bufsize=1)
        characters, transcript = queue.Queue(), []

        def read():
            while True:
                character = process.stdout.read(1)
                characters.put(character)
                if not character:
                    break

        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        try:
            deadline = time.monotonic() + 30
            while "[y/N]:" not in "".join(transcript):
                character = characters.get(timeout=max(0, deadline - time.monotonic()))
                self.assertTrue(character, "".join(transcript))
                transcript.append(character)
            mutate()
            sources, metadata = self.sources(), self.git_files()
            process.stdin.write("yes\n")
            process.stdin.flush()
            process.stdin.close()
            code = process.wait(timeout=30)
            reader.join(timeout=5)
            self.assertFalse(reader.is_alive())
            while not characters.empty():
                transcript.append(characters.get_nowait())
            return code, "".join(transcript), sources, metadata
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            if not process.stdin.closed:
                process.stdin.close()
            reader.join(timeout=5)
            process.stdout.close()

    def test_confirmation_external_branch_switch_is_blocked(self):
        for branch in ("main", "practice/other"):
            with self.subTest(branch=branch):
                if branch != "main":
                    self.git("branch", branch, "refs/heads/main")
                solve(self.root, "python", "hello")
                code, output, sources, metadata = self.live_reset(lambda: self.git("switch", branch))
                self.assertEqual(code, 2, output)
                self.assertEqual(self.sources(), sources)
                self.assertEqual(self.git_files(), metadata)
                self.assert_no_backups()
                self.git("switch", "practice/reset")

    def test_confirmation_external_source_edit_is_blocked(self):
        solve(self.root, "python", "hello")
        code, output, sources, metadata = self.live_reset(
            lambda: self.answer().write_bytes(b"# newer external learner edit\n"))
        self.assertEqual(code, 2, output)
        self.assertEqual(self.sources(), sources)
        self.assertEqual(self.git_files(), metadata)
        self.assert_no_backups()

    def test_confirmation_main_ref_move_uses_pinned_oid_or_refuses(self):
        solve(self.root, "python", "hello")
        self.git("add", "practice/python/exercises/hello.py")
        self.commit()
        learner_oid = self.git("rev-parse", "HEAD")
        code, output, sources, metadata = self.live_reset(
            lambda: self.git("update-ref", "refs/heads/main", learner_oid))
        self.assertIn(f"Reset baseline: refs/heads/main at {self.main_oid}", output)
        self.assertEqual(self.git_files(), metadata)
        if code == 0:
            self.assertEqual(self.answer().read_bytes(), self.baseline)
        else:
            self.assertEqual(code, 2, output)
            self.assertEqual(self.sources(), sources)
            self.assert_no_backups()


if __name__ == "__main__":
    unittest.main()
