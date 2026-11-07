"""Isolated black-box tests for the already-built root Rust CLI.

Build with `cargo build --offline`, or set POLYGLOT_BIN to another build.
No command in this suite operates on the repository's learner answers.
"""

import hashlib
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest

from git_fixture import isolated_git_env
from active_fixture import IDS, LANGUAGES, copy_active_fixture, exercise_path, solve, tool_overrides


REPO = Path(__file__).resolve().parents[1]
PYTHON_SOLUTION = '''def hello():
    print("Hello, World!")

def find_in_string(string, substring):
    return string.find(substring)

def length_of_last_word(text):
    words = text.split()
    return len(words[-1]) if words else 0
'''
RUST_SOLUTION = 'pub fn greeting() -> &\'static str { "Hello, World!" }\n'


class RustCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = Path(os.environ.get("POLYGLOT_BIN", REPO / "target/debug/polyglot")).absolute()
        if not cls.binary.is_file() or not os.access(cls.binary, os.X_OK):
            raise RuntimeError(
                f"Rust CLI binary is missing or not executable: {cls.binary}. "
                f"Run `cargo build --offline` in {REPO}, or set POLYGLOT_BIN "
                "to an already-built executable."
            )
        cargo = shutil.which("cargo")
        if cargo is None:
            raise RuntimeError("Install Cargo and put it on PATH to run the Rust adapter tests.")
        # Do not resolve rustup's cargo symlink: rustup dispatches by argv[0].
        cls.cargo = str(Path(cargo).absolute())
        cls.python = str(Path(sys.executable).absolute())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="polyglot cli tests ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "copied repository with spaces"
        self.cwd = self.base / "unrelated working directory"
        self.env = isolated_git_env()
        self.cwd.mkdir()
        copy_active_fixture(self.root)
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.env["CARGO_TERM_COLOR"] = "never"
        # Keep caller-specific build flags/target redirections out of fixtures.
        for key in ("CARGO_TARGET_DIR", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS"):
            self.env.pop(key, None)
        shutil.copy2(REPO / ".gitignore", self.root / ".gitignore")
        for args in (("init", "--initial-branch=main"), ("add", "."),
                     ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "commit", "--no-gpg-sign", "-m", "Fixture"),
                     ("switch", "-c", "practice/fixture")):
            self.assert_code(self.execute(["git", *args], cwd=self.root), 0)

    def directory(self, language):
        return self.root / "practice" / language

    def answer(self, language, name="hello"):
        return exercise_path(self.root, language, name)

    def sources(self):
        """Cargo artifacts are allowed; fixture source mutations are not."""
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if "target" not in path.relative_to(self.root).parts
            and ".git" not in path.relative_to(self.root).parts
            and path.is_file() and not path.is_symlink()
        }

    def git_files(self):
        directory = self.root / ".git"
        return {str(path.relative_to(directory)): path.read_bytes()
                for path in directory.rglob("*") if path.is_file()}

    def execute(self, command, *, cwd=None, env=None):
        return subprocess.run(
            [str(arg) for arg in command], cwd=cwd or self.cwd,
            env=self.env if env is None else env,
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=90,
        )

    def assert_code(self, result, expected):
        self.assertEqual(
            result.returncode, expected,
            f"command: {result.args!r}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def cli(self, *args, code=0, python=True, globals=(), env=None):
        command = [self.binary, "--root", self.root]
        if python:
            command += ["--python", self.python]
        command += ["--cargo", self.cargo, *tool_overrides(), *globals, *args]
        before = self.sources() if args and args[0] == "check" else None
        result = self.execute(command, env=env)
        if before is not None:
            self.assertEqual(self.sources(), before, "check mutated fixture sources")
        return self.assert_code(result, code)

    def solve(self, language):
        solve(self.root, language)

    def native(self, language, name=None):
        directory = self.directory(language)
        if language == "python":
            command = [self.python, "-B", "-m", "unittest", "discover", "-s", "tests", "-t", "."]
        else:
            command = [self.cargo, "test", "--offline", "--manifest-path",
                       directory / "Cargo.toml",
                       *(["--test", "practice_checks" if name == "hello" else name + "_checks"]
                         if name else ["--tests"]),
                       "--target-dir", directory / "target", "--", "--nocapture"]
        return self.execute(command, cwd=directory)

    def test_help_and_catalog_need_no_tools_or_writes(self):
        before = self.sources()
        env = {**self.env, "PATH": ""}
        missing = self.base / "missing tool"
        overrides = ("--python", missing, "--cargo", missing, *tool_overrides(missing))
        help_result = self.cli("--help", globals=overrides, env=env)
        self.assertIn("Global options", help_result.stdout)
        result = self.cli("list", globals=overrides, env=env)
        self.assertEqual([line.split("\t")[0] for line in result.stdout.splitlines()], list(IDS))
        self.assertIn("README/katas/hello_world.md", result.stdout)
        for language in LANGUAGES:
            with self.subTest(language=language):
                result = self.cli("list", "--language", language, globals=overrides, env=env)
                self.assertEqual([line.split("\t")[0] for line in result.stdout.splitlines()],
                                 [item for item in IDS if item.startswith(language + "/")])
        self.assertEqual(self.sources(), before)

    def test_invalid_arguments_do_not_write(self):
        before = self.sources()
        cases = [(), ("start",), ("check",), ("list", "extra"),
                 ("list", "--language"), ("list", "--language", "javascript"),
                 ("unknown",), ("start", "python"), ("start", "rust"),
                 ("check", "hello"), ("start", "python/hello", "extra"),
                 ("check", "python", "--python", self.python)]
        for selection in ("../python/hello", "python/../hello", "/python/hello",
                          "python/hello/", "python/nope", "javascript/hello", ""):
            cases += [(command, selection) for command in ("start", "check")]
        for args in cases:
            with self.subTest(args=args):
                self.cli(*args, code=2)
        for flag in ("--root", "--python", "--cargo", "--node", "--tsc", "--go", "--bash", "--lua"):
            with self.subTest(flag=flag):
                self.assert_code(self.execute([self.binary, flag]), 2)
        self.assertEqual(self.sources(), before)

    def test_start_validates_existing_files_without_writes(self):
        for language in ("python", "rust"):
            with self.subTest(language=language):
                before = self.sources()
                metadata = self.git_files()
                self.cli("start", language + "/hello")
                self.assertEqual(self.sources(), before)
                self.assertEqual(self.git_files(), metadata)
                edited = b"# edited learner bytes\r\n" if language == "python" else b"// edited\r\n"
                self.answer(language).write_bytes(edited)
                selections = [item for item in IDS if item.startswith(language + "/")]
                for selection in selections:
                    self.cli("start", selection)
                    self.assertEqual(self.answer(language).read_bytes(), edited)

    def test_concurrent_start_preserves_blank_and_edited_files(self):
        for language in ("python", "rust"):
            for edited in (False, True):
                with self.subTest(language=language, edited=edited):
                    if edited:
                        self.solve(language)
                    expected = self.sources()
                    metadata = self.git_files()
                    command = [str(self.binary), "--root", str(self.root), "--python", self.python,
                               "--cargo", self.cargo, "start", language + "/hello"]
                    processes = []
                    try:
                        for _ in range(4):
                            processes.append(subprocess.Popen(command, cwd=self.cwd, env=self.env,
                                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                              text=True))
                        for process in processes:
                            stdout, stderr = process.communicate(timeout=30)
                            self.assertEqual(process.returncode, 0, stdout + stderr)
                    finally:
                        for process in processes:
                            if process.poll() is None:
                                process.kill()
                                process.communicate()
                    self.assertEqual(self.sources(), expected)
                    self.assertEqual(self.git_files(), metadata)

    def test_missing_attempts_are_blocked_without_creation(self):
        for selection in IDS:
            language, name = selection.split("/")
            self.answer(language, name).unlink()
        for selection in (*IDS, "python", "rust"):
            with self.subTest(selection=selection):
                result = self.cli("check", selection, code=2)
                self.assertIn("Blocked:", result.stderr)
        self.assertFalse(self.answer("python").exists())
        self.assertFalse(self.answer("rust").exists())

    def test_missing_exercises_are_not_invented_by_start(self):
        for language in ("python", "rust"):
            with self.subTest(language=language):
                self.answer(language).unlink()
                before = self.sources()
                self.cli("start", language + "/hello", code=2)
                self.assertEqual(self.sources(), before)
                self.assertFalse(self.answer(language).exists())

    def test_answer_directories_are_rejected(self):
        for language in ("python", "rust"):
            with self.subTest(language=language):
                self.answer(language).unlink()
                self.answer(language).mkdir()
                for command in ("start", "check"):
                    self.cli(command, language + "/hello", code=2)
                self.assertEqual(list(self.answer(language).iterdir()), [])

    @unittest.skipUnless(os.name == "posix", "requires Unix symlinks")
    def test_answer_symlinks_are_rejected_without_outside_writes(self):
        outside = self.base / "outside answer"
        outside.write_bytes(b"untouched outside answer\n")
        for language in ("python", "rust"):
            with self.subTest(language=language):
                try:
                    self.answer(language).unlink()
                    self.answer(language).symlink_to(outside)
                except (OSError, NotImplementedError) as error:
                    self.skipTest(f"symlinks unavailable: {error}")
                for command in ("start", "check"):
                    self.cli(command, language + "/hello", code=2)
                self.assertTrue(self.answer(language).is_symlink())
                self.assertEqual(outside.read_bytes(), b"untouched outside answer\n")

    @unittest.skipUnless(os.name == "posix", "requires Unix symlinks")
    def test_parent_workspace_symlinks_are_rejected(self):
        for relative in ("practice/python", "practice/rust", "practice"):
            with self.subTest(relative=relative):
                original = self.root / relative
                outside = self.base / ("outside " + relative.replace("/", " "))
                original.rename(outside)
                try:
                    try:
                        original.symlink_to(outside, target_is_directory=True)
                    except (OSError, NotImplementedError) as error:
                        self.skipTest(f"symlinks unavailable: {error}")
                    before = {str(p.relative_to(outside)): p.read_bytes()
                              for p in outside.rglob("*") if p.is_file()}
                    languages = ("python", "rust") if relative == "practice" else (relative.split("/")[-1],)
                    for language in languages:
                        for command in ("start", "check"):
                            self.cli(command, language + "/hello", code=2)
                    self.assertEqual({str(p.relative_to(outside)): p.read_bytes()
                                      for p in outside.rglob("*") if p.is_file()}, before)
                finally:
                    if original.is_symlink():
                        original.unlink()
                    outside.rename(original)

    def test_python_blank_and_valid_match_native_runner(self):
        self.cli("start", "python/hello")
        for solved, expected in ((False, 1), (True, 0)):
            with self.subTest(solved=solved):
                if solved:
                    self.solve("python")
                result = self.cli("check", "python", code=expected)
                self.assertIn("Ran 5 tests", result.stderr)
                self.assert_code(self.native("python"), expected)

    def test_rust_blank_and_valid_match_native_runner(self):
        self.cli("start", "rust/hello")
        for solved, expected in ((False, 1), (True, 0)):
            with self.subTest(solved=solved):
                if solved:
                    self.solve("rust")
                result = self.cli("check", "rust", code=expected)
                self.assertIn("test result:", result.stdout)
                self.assert_code(self.native("rust"), 0 if solved else 101)
        self.cli("check", "rust/hello")

    def test_each_python_id_can_pass_with_siblings_blank(self):
        for selection in IDS[:5]:
            with self.subTest(selection=selection):
                name = selection.split("/")[1]
                starter = self.answer("python", name).read_text()
                self.cli("check", selection, code=1)
                solve(self.root, "python", name)
                self.cli("check", selection)
                self.cli("check", "python", code=1)
                self.answer("python", name).write_text(starter)

    def test_python_learner_syntax_and_assertion_failures(self):
        for source, diagnostic in (("def hello(:\n", "SyntaxError"),
                                   (PYTHON_SOLUTION.replace("Hello, World!", "wrong"), "AssertionError")):
            with self.subTest(diagnostic=diagnostic):
                self.answer("python").write_text(source)
                result = self.cli("check", "python/hello", code=1)
                self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_selected_python_is_independent_of_broken_or_missing_siblings(self):
        solve(self.root, "python", "hello")
        sibling = self.answer("python", "find_in_string")
        sibling_harness = self.directory("python") / "tests/test_find_in_string.py"
        for source in ("def broken(:\n", "raise RuntimeError('must not import sibling')\n", None):
            with self.subTest(source=source):
                if source is None:
                    sibling.unlink()
                    sibling_harness.unlink()
                else:
                    sibling.write_text(source)
                    sibling_harness.write_text("def broken_harness(:\n")
                before = self.sources()
                self.cli("start", "python/hello")
                self.cli("check", "python/hello")
                self.cli("practice", "python/hello")
                self.assert_code(self.execute(
                    [self.python, "-B", "-m", "unittest", "tests.test_hello"],
                    cwd=self.directory("python")), 0)
                self.assertEqual(self.sources(), before)
        self.cli("check", "python", code=2)

    def test_python_feedback_labels_actual_and_expected_output(self):
        self.answer("python").write_text(
            PYTHON_SOLUTION.replace('print("Hello, World!")', 'print("Hello, World!\\n")')
        )
        for result in (
            self.cli("check", "python/hello", code=1),
            self.assert_code(self.native("python"), 1),
        ):
            diagnostic = result.stdout + result.stderr
            self.assertIn(r"Your output: 'Hello, World!\n\n'", diagnostic)
            self.assertIn(r"Expected output: 'Hello, World!\n'", diagnostic)
            self.assertIn(r"Whitespace: \n = newline; \t = tab.", diagnostic)
            self.assertNotIn(" != ", diagnostic)

    def test_python_feedback_labels_result_and_return_value(self):
        cases = (
            (PYTHON_SOLUTION.replace("return string.find(substring)", "return -99"),
             "python/find_in_string", "Your result: -99", "Expected result: 8"),
            (PYTHON_SOLUTION.replace("return len(words[-1]) if words else 0", "return -99"),
             "python/length_of_last_word", "Your result: -99", "Expected result: 5"),
            (PYTHON_SOLUTION.replace('print("Hello, World!")', 'print("Hello, World!"); return 42'),
             "python/hello", "Your return value: 42", "Expected return value: None"),
            (PYTHON_SOLUTION.replace("return string.find(substring)", "return False"),
             "python/find_in_string", "Your result: False (type: bool)", "Expected result type: int"),
        )
        for source, target, actual, expected in cases:
            with self.subTest(target=target, actual=actual):
                self.answer("python", target.split("/")[1]).write_text(source)
                result = self.cli("check", target, code=1)
                diagnostic = result.stdout + result.stderr
                self.assertIn(actual, diagnostic)
                self.assertIn(expected, diagnostic)

    def test_rust_learner_compile_and_assertion_failures(self):
        for source, diagnostic in (("pub fn greeting() -> &'static str { 42 }\n", "mismatched types"),
                                   (RUST_SOLUTION.replace("Hello, World!", "wrong"), "assertion")):
            with self.subTest(diagnostic=diagnostic):
                self.answer("rust").write_text(source)
                result = self.cli("check", "rust/hello", code=1)
                self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_broken_python_harness_is_blocked(self):
        self.solve("python")
        harness = self.directory("python") / "tests/test_hello.py"
        for source in ("def broken(:\n", "raise RuntimeError('broken harness')\n"):
            with self.subTest(source=source):
                harness.write_text(source)
                self.cli("check", "python", code=2)

    def test_unknown_python_native_selector_is_blocked(self):
        self.solve("python")
        harness = self.directory("python") / "tests/test_hello.py"
        harness.write_text(harness.read_text().replace("def test_hello(", "def renamed_hello("))
        self.cli("check", "python/hello", code=2)

    def test_python_skips_cannot_report_success(self):
        self.solve("python")
        harness = self.directory("python") / "tests/test_hello.py"
        harness.write_text(harness.read_text().replace(
            "    def test_hello(", '    @unittest.skip("fixture skip")\n    def test_hello('
        ))
        self.cli("check", "python/hello", code=3)

    def test_broken_rust_manifest_and_harness_are_blocked(self):
        self.solve("rust")
        manifest = self.directory("rust") / "Cargo.toml"
        original = manifest.read_text()
        for source in ("not valid toml [\n", original.replace('name = "practice_checks"', 'name = "renamed"')):
            with self.subTest(manifest=source):
                manifest.write_text(source)
                self.cli("check", "rust", code=2)
        manifest.write_text(original)
        (self.directory("rust") / "checks.rs").write_text("this is not Rust;\n")
        self.cli("check", "rust", code=2)

    def test_rust_zero_or_ignored_tests_cannot_pass(self):
        self.solve("rust")
        harness = self.directory("rust") / "checks.rs"
        original = harness.read_text()
        for source, expected in ((original.replace("fn hello()", "fn renamed()"), 2),
                                 (original.replace("#[test]", "#[test]\n#[ignore]"), 3)):
            with self.subTest(source=source):
                harness.write_text(source)
                self.cli("check", "rust/hello", code=expected)

    def test_explicit_missing_tools_do_not_fall_back(self):
        for language, flag in (("python", "--python"), ("rust", "--cargo")):
            with self.subTest(language=language):
                self.solve(language)
                self.cli("check", language, globals=(flag, self.base / "missing executable"), code=2)

    @unittest.skipUnless(os.name == "posix", "requires Unix executable shims")
    def test_python_resolution_venv_override_path_and_bad_version(self):
        self.solve("python")
        venv_python = self.root / ".venv/bin/python"
        venv_python.parent.mkdir(parents=True)
        venv_python.symlink_to(self.python)
        result = self.cli("check", "python/hello", python=False)
        self.assertIn(str(venv_python), result.stdout)
        venv_python.unlink()
        venv_python.write_text("#!/bin/sh\nexit 7\n")
        venv_python.chmod(0o755)
        self.cli("check", "python/hello", python=False, code=2)
        result = self.cli("check", "python/hello")
        self.assertIn(self.python, result.stdout)
        venv_python.unlink()
        shim = self.base / "old python"
        shim.write_text('#!/bin/sh\nprintf \'%s\\n\' \'{"version": [3, 10, 0]}\'\n')
        shim.chmod(0o755)
        self.cli("check", "python/hello", globals=("--python", shim), code=2)
        path_bin = self.base / "path tools"
        path_bin.mkdir()
        (path_bin / "python3").symlink_to(self.python)
        self.cli("check", "python/hello", python=False, env={**self.env, "PATH": str(path_bin)})

    def test_python_stdout_cannot_spoof_structured_result(self):
        self.cli("start", "python/hello")
        with self.answer("python").open("a") as answer:
            answer.write('\nprint(\'Passed\\n{"outcome":"passed","ran":1}\\nOK\')\n')
        result = self.cli("check", "python/hello", code=1)
        self.assertIn('"outcome":"passed"', result.stdout)

    def test_python_early_exit_is_indeterminate(self):
        for statement in ("import sys; sys.exit(0)", "import os; os._exit(0)"):
            with self.subTest(statement=statement):
                self.answer("python").write_text(statement + "\n" + PYTHON_SOLUTION)
                self.cli("check", "python/hello", code=3)

    def test_python_checks_read_fresh_sources_despite_valid_timestamp_cache(self):
        for filename in ("exercises/hello.py", "tests/test_hello.py"):
            with self.subTest(filename=filename):
                self.solve("python")
                source = self.directory("python") / filename
                original = source.read_bytes()
                changed = original.replace(b"Hello, World!", b"Wrong, World!")
                self.assertNotEqual(changed, original)
                self.assertEqual(len(changed), len(original))
                timestamp_ns = 1_700_000_000 * 1_000_000_000
                os.utime(source, ns=(timestamp_ns, timestamp_ns))
                cached = Path(py_compile.compile(
                    str(source), doraise=True,
                    invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP,
                ))
                self.assertTrue(cached.is_file())
                # A normal loader considers this old passing bytecode valid.
                source.write_bytes(changed)
                os.utime(source, ns=(timestamp_ns, timestamp_ns))
                self.assertEqual(source.stat().st_mtime_ns, timestamp_ns)
                try:
                    result = self.cli("check", "python/hello", code=1)
                    self.assertIn("AssertionError", result.stdout + result.stderr)
                finally:
                    source.write_bytes(original)
                    cached.unlink()

    @unittest.skipUnless(os.name == "posix", "requires Unix symlinks")
    def test_nested_rust_target_symlinks_are_blocked_before_outside_writes(self):
        self.solve("rust")
        target = self.directory("rust") / "target"
        for relative in ("debug", "debug/.fingerprint"):
            with self.subTest(relative=relative):
                with tempfile.TemporaryDirectory(prefix="polyglot outside target ") as name:
                    outside = Path(name)
                    (outside / "sentinel").write_bytes(b"do not change\n")
                    link = target / relative
                    link.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        link.symlink_to(outside, target_is_directory=True)
                    except (OSError, NotImplementedError) as error:
                        self.skipTest(f"symlinks unavailable: {error}")
                    before = {str(p.relative_to(outside)): hashlib.sha256(p.read_bytes()).hexdigest()
                              if p.is_file() else None
                              for p in outside.rglob("*")}
                    try:
                        try:
                            self.cli("check", "rust/hello", code=2)
                        finally:
                            self.assertEqual(
                                {str(p.relative_to(outside)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 if p.is_file() else None for p in outside.rglob("*")}, before,
                                "Rust check wrote through a nested target symlink",
                            )
                    finally:
                        shutil.rmtree(target)

    def test_missing_and_stale_rust_lockfiles_are_blocked_without_source_writes(self):
        self.solve("rust")
        lock = self.directory("rust") / "Cargo.lock"
        original_lock = lock.read_bytes()
        with self.subTest(lockfile="missing"):
            lock.unlink()
            self.cli("check", "rust", code=2)
            self.assertFalse(lock.exists(), "check must not generate a lockfile")
        with self.subTest(lockfile="stale"):
            lock.write_bytes(original_lock)
            manifest = self.directory("rust") / "Cargo.toml"
            original_manifest = manifest.read_bytes()
            self.assertIn(b'version = "0.1.0"', original_manifest)
            manifest.write_bytes(original_manifest.replace(b'version = "0.1.0"',
                                                          b'version = "0.2.0"'))
            self.cli("check", "rust", code=2)
            self.assertEqual(lock.read_bytes(), original_lock)


if __name__ == "__main__":
    unittest.main()
