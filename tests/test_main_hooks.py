"""Optional main-branch hooks, exercised only in disposable Git repositories."""

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest

from git_fixture import isolated_git_env


REPO = Path(__file__).resolve().parents[1]


class MainHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="polyglot hook tests ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "fixture repository"
        self.root.mkdir()
        self.global_config = self.base / "isolated global config"
        self.global_config.write_text("")
        self.env = isolated_git_env()
        self.env["GIT_CONFIG_GLOBAL"] = str(self.global_config)
        shutil.copytree(REPO / ".githooks", self.root / ".githooks")
        shutil.copy2(REPO / "Makefile", self.root / "Makefile")
        shutil.copy2(REPO / ".gitignore", self.root / ".gitignore")
        for relative in ("practice/python/starter.py", "practice/rust/starter.rs", "docs.md"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"baseline fixture bytes\n")
        self.git("init", "--initial-branch=main")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--no-gpg-sign", "-m", "Fixture")

    def run_command(self, *args, cwd=None, code=0):
        result = subprocess.run(args, cwd=cwd or self.root, env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, code,
                         f"{result.args!r}\n{result.stdout}\n{result.stderr}")
        return result.stdout + result.stderr

    def git(self, *args, cwd=None):
        return self.run_command("git", *args, cwd=cwd).strip()

    def snapshot(self, root=None, exclude_installed=False):
        root = root or self.root
        result = {}
        for path in root.rglob("*"):
            relative = str(path.relative_to(root))
            if exclude_installed and relative == ".git/hooks/pre-commit":
                continue
            if path.is_symlink():
                result[relative] = ("symlink", os.readlink(path))
            elif path.is_file():
                result[relative] = (stat.S_IMODE(path.stat().st_mode), path.read_bytes())
        return result

    def hook(self, *, blocked):
        before = self.snapshot()
        output = self.run_command("sh", ".githooks/pre-commit", code=1 if blocked else 0)
        self.assertEqual(self.snapshot(), before, "hook changed index, metadata or working files")
        if blocked:
            self.assertIn("Polyglot:", output)
        return output

    def hook_path(self, cwd=None):
        path = Path(self.git("rev-parse", "--git-path", "hooks/pre-commit", cwd=cwd))
        return path if path.is_absolute() else (cwd or self.root) / path

    def assert_installed(self, path):
        self.assertFalse(path.is_symlink())
        self.assertEqual(path.read_bytes(), (self.root / ".githooks/pre-commit").read_bytes())
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o755)

    def test_staged_legacy_starters_on_main_are_blocked(self):
        for relative in ("practice/python/starter.py", "practice/rust/starter.rs"):
            with self.subTest(path=relative):
                (self.root / relative).write_bytes(b"staged learner edit\n")
                self.git("add", "--", relative)
                output = self.hook(blocked=True)
                self.assertIn("git switch -c", output)
                self.git("restore", "--staged", "--", relative)

    def test_force_added_ignored_answers_on_main_are_blocked(self):
        for relative in ("practice/python/answers.py", "practice/rust/answers.rs"):
            with self.subTest(path=relative):
                (self.root / relative).write_bytes(b"ignored learner answer\n")
                self.git("check-ignore", "--", relative)
                self.git("add", "-f", "--", relative)
                self.hook(blocked=True)
                self.git("restore", "--staged", "--", relative)

    def test_future_exercises_with_unusual_names_on_main_are_blocked(self):
        for relative in ("practice/python/exercises/foo.py",
                         "practice/rust/exercises/nested/with spaces.rs",
                         "practice/python/exercises/with\nnewline.py"):
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"future exercise\n")
                self.git("add", "--", relative)
                self.hook(blocked=True)
                self.git("restore", "--staged", "--", relative)

    def test_staged_protected_deletion_on_main_is_blocked(self):
        self.git("rm", "practice/python/starter.py")
        self.hook(blocked=True)
        self.assertFalse((self.root / "practice/python/starter.py").exists())

    def test_main_tag_does_not_bypass_protected_main_deletion(self):
        self.git("tag", "main")
        self.git("rm", "practice/python/starter.py")
        self.hook(blocked=True)

    def test_staged_rename_out_of_protected_path_on_main_is_blocked(self):
        self.git("mv", "practice/python/starter.py", "renamed outside exercises.py")
        self.hook(blocked=True)
        self.assertEqual((self.root / "renamed outside exercises.py").read_bytes(),
                         b"baseline fixture bytes\n")

    def test_nonprotected_staged_docs_on_main_are_allowed(self):
        (self.root / "docs.md").write_text("documentation update\n")
        self.git("add", "docs.md")
        self.hook(blocked=False)

    def test_protected_staged_changes_on_feature_branch_are_allowed(self):
        self.git("switch", "-c", "practice/fixture")
        (self.root / "practice/python/starter.py").write_text("feature edit\n")
        self.git("add", "practice/python/starter.py")
        self.hook(blocked=False)

    def test_unstaged_protected_edits_do_not_block_main(self):
        (self.root / "practice/python/starter.py").write_text("unstaged learner edit\n")
        (self.root / "practice/python/answers.py").write_text("ignored learner answer\n")
        self.hook(blocked=False)
        (self.root / "docs.md").write_text("staged documentation\n")
        self.git("add", "docs.md")
        self.hook(blocked=False)

    def test_detached_head_is_blocked_even_without_staged_changes(self):
        self.git("switch", "--detach")
        self.assertIn("detached HEAD", self.hook(blocked=True))

    @unittest.skipUnless(shutil.which("make"), "requires make")
    def test_make_install_hooks_is_opt_in_executable_and_idempotent(self):
        hook = self.hook_path()
        self.assertFalse(hook.exists(), "fixture must not install hooks implicitly")
        before = self.snapshot(exclude_installed=True)
        self.run_command("make", "install-hooks")
        self.assert_installed(hook)
        self.assertEqual(self.snapshot(exclude_installed=True), before)
        installed = self.snapshot()
        self.run_command("make", "install-hooks")
        self.assertEqual(self.snapshot(), installed)

    def test_linked_worktree_installs_to_git_resolved_hook_path(self):
        linked = self.base / "linked worktree"
        self.git("worktree", "add", "-b", "practice/linked", str(linked), "main")
        hook = self.hook_path(cwd=linked)
        self.assertEqual(hook.resolve(), self.hook_path().resolve())
        before, linked_before = self.snapshot(exclude_installed=True), self.snapshot(linked)
        self.run_command("sh", ".githooks/install.sh", cwd=linked)
        self.assert_installed(hook)
        self.assertEqual(self.snapshot(exclude_installed=True), before)
        self.assertEqual(self.snapshot(linked), linked_before)

    def test_installer_refuses_different_existing_hook_without_changes(self):
        hook = self.hook_path()
        hook.write_bytes(b"#!/bin/sh\n# existing custom hook\nexit 0\n")
        hook.chmod(0o700)
        before = self.snapshot()
        self.run_command("sh", ".githooks/install.sh", code=1)
        self.assertEqual(self.snapshot(), before)

    @unittest.skipUnless(os.name == "posix", "requires Unix symlinks")
    def test_installer_refuses_matching_and_dangling_symlinks(self):
        hook = self.hook_path()
        for target in (self.root / ".githooks/pre-commit", self.base / "missing hook"):
            with self.subTest(target=str(target)):
                hook.symlink_to(target)
                before = self.snapshot()
                self.run_command("sh", ".githooks/install.sh", code=1)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(os.readlink(hook), str(target))
                hook.unlink()

    def test_installer_refuses_global_core_hooks_path_without_changes(self):
        custom = self.base / "custom hooks"
        custom.mkdir()
        existing = custom / "pre-commit"
        existing.write_bytes(b"#!/bin/sh\nexit 0\n")
        self.global_config.write_text(f'[core]\n\thooksPath = "{custom}"\n')
        self.assertEqual(self.git("config", "--get", "core.hooksPath"), str(custom))
        before = self.snapshot(self.base)
        output = self.run_command("sh", ".githooks/install.sh", code=1)
        self.assertIn("core.hooksPath", output)
        self.assertEqual(self.snapshot(self.base), before)


if __name__ == "__main__":
    unittest.main()
