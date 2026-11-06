"""Exercise actual fixture setup with caller Git context pointing at temp repos."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from git_fixture import isolated_git_env
import test_branch_policy
import test_interactive_cli
import test_main_hooks
import test_rust_cli


class GitFixtureIsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="polyglot caller isolation ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.caller = self.base / "disposable caller repository"
        self.caller.mkdir()
        self.env = isolated_git_env()
        (self.caller / "source.txt").write_bytes(b"caller baseline\n")
        self.git("init", "--initial-branch=main")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--no-gpg-sign", "-m", "Caller")
        (self.caller / "source.txt").write_bytes(b"caller staged work\n")
        self.git("add", "source.txt")
        (self.caller / "source.txt").write_bytes(b"caller unstaged work\n")
        (self.caller / "untracked.txt").write_bytes(b"caller untracked work\n")
        self.hooks = self.base / "caller global hooks"
        self.hooks.mkdir()
        hook = self.hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 97\n")
        hook.chmod(0o755)
        self.config = self.base / "caller global config"
        self.config.write_text(f'[core]\n\thooksPath = "{self.hooks}"\n')

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.caller, env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def assert_setups_isolated(self, context):
        # Import modules, not TestCase classes, so discovery does not rerun their tests here.
        suites = (test_rust_cli.RustCliTests, test_interactive_cli.InteractiveCliTests,
                  test_branch_policy.BranchPolicyTests, test_main_hooks.MainHookTests)
        poison = {**context, "GIT_CONFIG_GLOBAL": str(self.config),
                  "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath",
                  "GIT_CONFIG_VALUE_0": str(self.hooks), "GIT_FUTURE_CONTEXT": "discard me"}
        for suite in suites:
            with self.subTest(suite=suite.__name__):
                before = {str(p.relative_to(self.caller)): p.read_bytes()
                          for p in self.caller.rglob("*") if p.is_file()}
                fixture = suite(methodName="runTest")
                try:
                    with patch.dict(os.environ, poison):
                        fixture.setUp()
                    self.assertTrue((fixture.root / ".git/HEAD").is_file())
                    result = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                            cwd=fixture.root, env=fixture.env,
                                            capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(Path(result.stdout.strip()).resolve(), fixture.root.resolve())
                    self.assertNotIn("GIT_FUTURE_CONTEXT", fixture.env)
                    self.assertNotIn("GIT_CONFIG_COUNT", fixture.env)
                    self.assertEqual(fixture.env["GIT_CONFIG_NOSYSTEM"], "1")
                    for key in context:
                        self.assertNotIn(key, fixture.env)
                finally:
                    self.assertTrue(fixture.doCleanups())
                    self.assertEqual({str(p.relative_to(self.caller)): p.read_bytes()
                                      for p in self.caller.rglob("*") if p.is_file()}, before,
                                     "fixture setup modified caller HEAD/refs/index/config/sources")

    def test_git_dir_is_not_inherited_by_fixture_setups(self):
        self.assert_setups_isolated({"GIT_DIR": str(self.caller / ".git")})

    def test_work_tree_is_not_inherited_by_fixture_setups(self):
        self.assert_setups_isolated({"GIT_WORK_TREE": str(self.caller)})

    def test_index_file_is_not_inherited_by_fixture_setups(self):
        self.assert_setups_isolated({"GIT_INDEX_FILE": str(self.caller / ".git/index")})

    def test_combined_git_context_is_not_inherited_by_fixture_setups(self):
        self.assert_setups_isolated({"GIT_DIR": str(self.caller / ".git"),
                                    "GIT_WORK_TREE": str(self.caller),
                                    "GIT_INDEX_FILE": str(self.caller / ".git/index"),
                                    "GIT_COMMON_DIR": str(self.caller / ".git")})


if __name__ == "__main__":
    unittest.main()
