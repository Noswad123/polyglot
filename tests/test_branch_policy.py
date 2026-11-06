"""Black-box branch policy tests. All Git mutations use disposable repositories."""

import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from git_fixture import isolated_git_env
from active_fixture import copy_active_fixture, exercise_path, solve


REPO = Path(__file__).resolve().parents[1]


class BranchFixture:
    @classmethod
    def setUpClass(cls):
        cls.binary = Path(os.environ.get("POLYGLOT_BIN", REPO / "target/debug/polyglot")).absolute()
        if not cls.binary.is_file() or not os.access(cls.binary, os.X_OK):
            raise RuntimeError(f"Build the CLI first, or set POLYGLOT_BIN: {cls.binary}")
        cls.python = str(Path(sys.executable).absolute())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="polyglot branch policy ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "fixture repository"
        self.env = {**isolated_git_env(), "PYTHONDONTWRITEBYTECODE": "1"}
        copy_active_fixture(self.root)
        self.git("init", "--initial-branch=main")
        self.git("add", ".")
        self.commit()

    def git(self, *args, root=None, code=0):
        result = subprocess.run(["git", "--no-optional-locks", *args], cwd=root or self.root,
                                env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout.strip()

    def commit(self):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--no-gpg-sign", "-m", "Fixture")

    def command(self, *args):
        return [str(self.binary), "--root", str(self.root), "--python", self.python,
                "--cargo", str(self.base / "missing cargo"), *args]

    def cli(self, *args, input="", code=0, env=None):
        result = subprocess.run(self.command(*args), cwd=self.base, env=env or self.env,
                                input=input, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, code,
                         f"{result.args!r}\n{result.stdout}\n{result.stderr}")
        return result.stdout + result.stderr

    def sources(self):
        return {str(p.relative_to(self.root)): p.read_bytes() if p.is_file() else None
                for p in self.root.rglob("*") if ".git" not in p.relative_to(self.root).parts}

    def git_files(self):
        # Include index, config, reflogs and refs, not just the current branch name.
        directory = self.root / ".git"
        if not directory.is_dir():
            return {}
        return {str(p.relative_to(directory)): p.read_bytes()
                for p in directory.rglob("*") if p.is_file()}

    def assert_blocked(self, *args, env=None):
        sources, metadata = self.sources(), self.git_files()
        output = self.cli(*args, input="q\n", code=2, env=env)
        self.assertEqual(self.sources(), sources, output)
        self.assertEqual(self.git_files(), metadata, output)
        return output

    def answer(self, language="python"):
        return exercise_path(self.root, language)

    def legacy_answer(self):
        return self.root / "practice/python/answers.py"


class BranchPolicyTests(BranchFixture, unittest.TestCase):
    def test_clean_main_explicit_target_creates_language_branch(self):
        main, before = self.git("rev-parse", "main"), self.sources()
        output = self.cli("practice", "python/hello", input="q\n")
        self.assertIn("Created practice branch", output)
        self.assertRegex(self.git("branch", "--show-current"), r"^practice/python-.+")
        self.assertEqual(self.git("rev-parse", "main"), main)
        self.assertEqual(self.git("rev-parse", "HEAD"), main)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.sources(), before)

    def test_clean_main_menu_selection_creates_rust_branch(self):
        main, before = self.git("rev-parse", "main"), self.sources()
        output = self.cli("practice", input="2\nq\n")
        self.assertIn("Created practice branch", output)
        self.assertRegex(self.git("branch", "--show-current"), r"^practice/rust-.+")
        self.assertEqual(self.git("rev-parse", "main"), main)
        self.assertEqual(self.sources(), before)

    def test_root_autobranch_ignores_poisoned_git_context(self):
        decoy = self.base / "decoy caller repository"
        shutil.copytree(self.root, decoy)
        decoy_before = {str(p.relative_to(decoy)): p.read_bytes()
                        for p in decoy.rglob("*") if p.is_file()}
        before, main = self.sources(), self.git("rev-parse", "refs/heads/main")
        poison = {**self.env, "GIT_DIR": str(decoy / ".git"),
                  "GIT_WORK_TREE": str(decoy), "GIT_INDEX_FILE": str(decoy / ".git/index"),
                  "GIT_COMMON_DIR": str(decoy / ".git")}
        output = self.cli("practice", "python", input="q\n", env=poison)
        self.assertIn("Created practice branch", output)
        self.assertRegex(self.git("branch", "--show-current"), r"^practice/python-.+")
        self.assertEqual(self.git("rev-parse", "refs/heads/main"), main)
        self.assertEqual(self.git("rev-parse", "HEAD"), main)
        self.assertEqual(self.sources(), before)
        self.assertEqual({str(p.relative_to(decoy)): p.read_bytes()
                          for p in decoy.rglob("*") if p.is_file()}, decoy_before)

    def test_generated_names_are_unique(self):
        self.cli("practice", "python", input="q\n")
        first = self.git("branch", "--show-current")
        self.git("switch", "main")
        self.cli("practice", "python", input="q\n")
        second = self.git("branch", "--show-current")
        self.assertNotEqual(first, second)
        self.assertRegex(second, r"^practice/python-.+")
        self.assertEqual(len(self.git("for-each-ref", "--format=%(refname)", "refs/heads").splitlines()), 3)

    def test_existing_nonmain_dirty_branch_is_reused(self):
        self.git("switch", "-c", "feature/learner")
        (self.root / "notes.txt").write_text("keep untracked\n")
        starter = self.answer()
        starter.write_bytes(starter.read_bytes() + b"\n# tracked learner edit\n")
        self.git("add", "practice/python/exercises/hello.py")
        self.legacy_answer().write_text("# ignored learner answer\n")
        before, metadata = self.sources(), self.git_files()
        output = self.cli("practice", "python", input="q\n")
        self.assertIn("Using practice branch", output)
        self.assertNotIn("Created practice branch", output)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_direct_start_on_main_is_blocked_without_switch(self):
        output = self.assert_blocked("start", "python/hello")
        self.assertIn("main", output.lower())
        self.assertRegex(output.lower(), r"git switch|git checkout")

    def test_direct_start_on_nonmain_does_not_create_branch(self):
        self.git("switch", "-c", "feature/direct")
        metadata = self.git_files()
        self.cli("start", "python/hello")
        self.assertEqual(self.git_files(), metadata)
        self.assertTrue(self.answer().is_file())

    def test_dirty_tracked_main_is_blocked(self):
        starter = self.answer()
        starter.write_bytes(starter.read_bytes() + b"\n# do not lose\n")
        output = self.assert_blocked("practice", "python")
        self.assertRegex(output.lower(), r"git switch|git checkout")

    def test_untracked_main_is_blocked(self):
        (self.root / "untracked notes").write_bytes(b"keep these notes\n")
        self.assert_blocked("practice", "python")

    def test_staged_main_is_blocked(self):
        (self.root / "staged notes").write_bytes(b"keep staged notes\n")
        self.git("add", "staged notes")
        self.assert_blocked("practice", "python")

    def test_ignored_files_do_not_make_main_dirty(self):
        self.legacy_answer().write_bytes(b"# preserve ignored answer\n")
        (self.root / ".cache").write_bytes(b"ignored cache\n")
        before = self.sources()
        self.cli("practice", "python", input="q\n")
        self.assertRegex(self.git("branch", "--show-current"), r"^practice/python-.+")
        self.assertEqual(self.sources(), before)

    def test_detached_head_is_blocked(self):
        self.git("switch", "--detach")
        for command in ("start", "practice"):
            self.assert_blocked(command, "python/hello")

    def test_unborn_named_branch_is_blocked(self):
        shutil.rmtree(self.root / ".git")
        self.git("init", "--initial-branch=feature/unborn")
        for command in ("start", "practice"):
            self.assert_blocked(command, "python/hello")

    def test_nonrepository_is_blocked_without_git_init(self):
        shutil.rmtree(self.root / ".git")
        for command in ("start", "practice"):
            self.assert_blocked(command, "python/hello")
        self.assertFalse((self.root / ".git").exists())

    def test_nested_root_is_not_treated_as_git_root(self):
        outer = self.root
        nested = outer / "nested"
        nested.mkdir()
        shutil.copytree(outer / "practice", nested / "practice")
        shutil.copytree(outer / "README", nested / "README")
        self.git("add", "nested")
        self.commit()
        self.git("switch", "-c", "feature/nested")
        metadata = self.git_files()
        self.root = nested
        for command in ("start", "practice"):
            self.assert_blocked(command, "python/hello")
        self.root = outer
        self.assertEqual(self.git_files(), metadata)

    def test_invalid_targets_quit_and_eof_do_not_mutate_git(self):
        before, metadata = self.sources(), self.git_files()
        for target in ("go/hello", "python/nope", "../python/hello", "hello", ""):
            self.cli("practice", target, code=2)
        for input in ("", "q\n", "quit\n", "invalid\nq\n"):
            self.cli("practice", input=input)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_missing_exercise_does_not_autobranch(self):
        self.answer().unlink()
        self.git("add", "-u")
        self.commit()
        self.assert_blocked("practice", "python")

    def test_conflicting_answer_does_not_autobranch(self):
        self.answer().unlink()
        self.answer().mkdir()
        self.assert_blocked("practice", "python")

    def test_missing_git_blocks_practice_and_start(self):
        self.git("switch", "-c", "practice/no-git")
        env = {**self.env, "PATH": ""}
        for command in ("start", "practice"):
            output = self.assert_blocked(command, "python/hello", env=env)
            self.assertIn("git", output.lower())

    def test_read_only_and_check_need_neither_git_nor_nonmain(self):
        solve(self.root, "python", "hello")
        before, metadata = self.sources(), self.git_files()
        env = {**self.env, "PATH": ""}
        for repository in (True, False):
            if not repository:
                shutil.rmtree(self.root / ".git")
            for args in (("list",), ("questions",), ("question", "hello-world"),
                         ("show", "python/hello"), ("hint", "python/hello"),
                         ("check", "python/hello")):
                self.cli(*args, env=env)
            self.assertEqual(self.sources(), before)
            self.assertEqual(self.git_files(), metadata if repository else {})

    def test_linked_worktree_supports_exact_root(self):
        worktree = self.base / "linked worktree"
        self.git("worktree", "add", "-b", "practice/linked", str(worktree), "main")
        self.root = worktree
        before = self.git("rev-parse", "HEAD")
        output = self.cli("practice", "python", input="q\n")
        self.assertIn("Using practice branch", output)
        self.assertEqual(self.git("branch", "--show-current"), "practice/linked")
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertTrue(self.answer().is_file())

    def test_live_session_external_main_switch_blocks_actions_but_allows_hint_quit(self):
        self.git("switch", "-c", "practice/live")
        process = subprocess.Popen(self.command("practice", "python/find_in_string"),
                                   cwd=self.base, env=self.env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, bufsize=1)
        lines, transcript = queue.Queue(), []

        def read_lines():
            try:
                for line in process.stdout:
                    lines.put(line)
            finally:
                lines.put(None)

        reader = threading.Thread(target=read_lines, daemon=True)
        reader.start()

        def wait_for(marker):
            deadline = time.monotonic() + 30
            while True:
                try:
                    line = lines.get(timeout=max(0, deadline - time.monotonic()))
                except queue.Empty:
                    self.fail(f"Timed out waiting for {marker!r}: {''.join(transcript)}")
                if line is None:
                    self.fail(f"CLI exited before {marker!r}: {''.join(transcript)}")
                transcript.append(line)
                if marker in line:
                    return

        try:
            wait_for("Exercise: python/find_in_string")
            self.git("switch", "main")
            before, metadata = self.sources(), self.git_files()
            for action in ("check", "next", "previous", "language rust"):
                process.stdin.write(action + "\n")
                process.stdin.flush()
                wait_for("Blocked:")
                self.assertEqual(self.sources(), before)
                self.assertEqual(self.git_files(), metadata)
            process.stdin.write("hint\nprompt\nq\n")
            process.stdin.flush()
            process.stdin.close()
            self.assertEqual(process.wait(timeout=30), 0)
            reader.join(timeout=5)
            self.assertFalse(reader.is_alive())
            while not lines.empty():
                line = lines.get_nowait()
                if line is not None:
                    transcript.append(line)
            output = "".join(transcript)
            self.assertIn("Hint:", output)
            self.assertNotIn("Created practice branch", output)
            self.assertNotIn("Exercise: rust/hello", output)
            self.assertIn("Exercise: python/find_in_string", output)
            self.assertNotIn("Exercise: python/length_of_last_word", output)
            self.assertEqual(self.sources(), before)
            self.assertEqual(self.git_files(), metadata)
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            if not process.stdin.closed:
                process.stdin.close()
            reader.join(timeout=5)
            process.stdout.close()


if __name__ == "__main__":
    unittest.main()
