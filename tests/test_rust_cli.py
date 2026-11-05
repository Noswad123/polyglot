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


REPO = Path(__file__).resolve().parents[1]
IDS = (
    "python/hello",
    "python/find_in_string",
    "python/length_of_last_word",
    "rust/hello",
)
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
        self.cwd.mkdir()
        for language, names in {
            "python": ("starter.py", "test_exercises.py", "README.md"),
            "rust": ("Cargo.toml", "Cargo.lock", "starter.rs", "checks.rs"),
        }.items():
            destination = self.root / "practice" / language
            destination.mkdir(parents=True)
            for name in names:
                shutil.copy2(REPO / "practice" / language / name, destination / name)
        rust_readme = REPO / "practice/rust/README.md"
        if rust_readme.is_file():
            shutil.copy2(rust_readme, self.directory("rust") / "README.md")
        else:
            (self.directory("rust") / "README.md").write_text("Rust fixture prompt.\n")
        self.env = os.environ.copy()
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.env["CARGO_TERM_COLOR"] = "never"
        # Keep caller-specific build flags/target redirections out of fixtures.
        for key in ("CARGO_TARGET_DIR", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS"):
            self.env.pop(key, None)

    def directory(self, language):
        return self.root / "practice" / language

    def answer(self, language):
        return self.directory(language) / ("answers.py" if language == "python" else "answers.rs")

    def sources(self):
        """Cargo artifacts are allowed; fixture source mutations are not."""
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if "target" not in path.relative_to(self.root).parts
            and path.is_file() and not path.is_symlink()
        }

    def execute(self, command, *, cwd=None, env=None):
        return subprocess.run(
            [str(arg) for arg in command], cwd=cwd or self.cwd,
            env=self.env if env is None else env,
            capture_output=True, text=True, timeout=90,
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
        command += ["--cargo", self.cargo, *globals, *args]
        before = self.sources() if args and args[0] == "check" else None
        result = self.execute(command, env=env)
        if before is not None:
            self.assertEqual(self.sources(), before, "check mutated fixture sources")
        return self.assert_code(result, code)

    def solve(self, language):
        self.answer(language).write_text(
            PYTHON_SOLUTION if language == "python" else RUST_SOLUTION
        )

    def native(self, language):
        directory = self.directory(language)
        if language == "python":
            command = [self.python, "-B", "-m", "unittest", "-v", "test_exercises"]
        else:
            command = [self.cargo, "test", "--offline", "--manifest-path",
                       directory / "Cargo.toml", "--test", "practice_checks",
                       "--target-dir", directory / "target", "--", "--nocapture"]
        return self.execute(command, cwd=directory)

    def test_help_and_catalog_need_no_tools_or_writes(self):
        before = self.sources()
        env = {**self.env, "PATH": ""}
        missing = self.base / "missing tool"
        overrides = ("--python", missing, "--cargo", missing)
        help_result = self.cli("--help", globals=overrides, env=env)
        self.assertIn("Global options", help_result.stdout)
        result = self.cli("list", globals=overrides, env=env)
        self.assertEqual([line.split("\t")[0] for line in result.stdout.splitlines()], list(IDS))
        self.assertIn("practice/rust/README.md", result.stdout)
        for language in ("python", "rust"):
            with self.subTest(language=language):
                result = self.cli("list", "--language", language, globals=overrides, env=env)
                self.assertEqual([line.split("\t")[0] for line in result.stdout.splitlines()],
                                 [item for item in IDS if item.startswith(language + "/")])
        self.assertEqual(self.sources(), before)

    def test_invalid_arguments_do_not_write(self):
        before = self.sources()
        cases = [(), ("start",), ("check",), ("list", "extra"),
                 ("list", "--language"), ("list", "--language", "go"),
                 ("unknown",), ("start", "python"), ("start", "rust"),
                 ("check", "hello"), ("start", "python/hello", "extra"),
                 ("check", "python", "--python", self.python)]
        for selection in ("../python/hello", "python/../hello", "/python/hello",
                          "python/hello/", "python/nope", "go/hello", ""):
            cases += [(command, selection) for command in ("start", "check")]
        for args in cases:
            with self.subTest(args=args):
                self.cli(*args, code=2)
        for flag in ("--root", "--python", "--cargo"):
            with self.subTest(flag=flag):
                self.assert_code(self.execute([self.binary, flag]), 2)
        self.assertEqual(self.sources(), before)

    def test_start_copies_exact_bytes_and_preserves_shared_answers(self):
        for language, starter in (("python", "starter.py"), ("rust", "starter.rs")):
            with self.subTest(language=language):
                self.cli("start", language + "/hello")
                self.assertEqual(self.answer(language).read_bytes(),
                                 (self.directory(language) / starter).read_bytes())
                edited = b"# edited learner bytes\r\n" if language == "python" else b"// edited\r\n"
                self.answer(language).write_bytes(edited)
                selections = IDS[:3] if language == "python" else IDS[3:]
                for selection in selections:
                    self.cli("start", selection)
                    self.assertEqual(self.answer(language).read_bytes(), edited)

    def test_concurrent_start_preserves_created_and_edited_answers(self):
        for language, starter in (("python", "starter.py"), ("rust", "starter.rs")):
            for edited in (False, True):
                with self.subTest(language=language, edited=edited):
                    if edited:
                        self.solve(language)
                    expected = (self.answer(language) if edited else
                                self.directory(language) / starter).read_bytes()
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
                    self.assertEqual(self.answer(language).read_bytes(), expected)

    def test_missing_attempts_are_blocked_without_creation(self):
        for selection in (*IDS, "python", "rust"):
            with self.subTest(selection=selection):
                result = self.cli("check", selection, code=2)
                self.assertIn("start", result.stderr)
        self.assertFalse(self.answer("python").exists())
        self.assertFalse(self.answer("rust").exists())

    def test_missing_starters_do_not_create_answers(self):
        for language, starter in (("python", "starter.py"), ("rust", "starter.rs")):
            with self.subTest(language=language):
                (self.directory(language) / starter).unlink()
                before = self.sources()
                self.cli("start", language + "/hello", code=2)
                self.assertEqual(self.sources(), before)
                self.assertFalse(self.answer(language).exists())

    def test_answer_directories_are_rejected(self):
        for language in ("python", "rust"):
            with self.subTest(language=language):
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
                self.assertIn("Ran 3 tests", result.stderr)
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
        replacements = (
            ('raise NotImplementedError("Implement hello")', 'print("Hello, World!")'),
            ('raise NotImplementedError("Implement find_in_string")', 'return string.find(substring)'),
            ('raise NotImplementedError("Implement length_of_last_word")',
             'return len(text.split()[-1]) if text.split() else 0'),
        )
        starter = (self.directory("python") / "starter.py").read_text()
        for selection, (old, new) in zip(IDS[:3], replacements):
            with self.subTest(selection=selection):
                self.assertIn(old, starter)
                self.answer("python").write_text(starter.replace(old, new))
                self.cli("check", selection)
                self.cli("check", "python", code=1)

    def test_python_learner_syntax_and_assertion_failures(self):
        for source, diagnostic in (("def hello(:\n", "SyntaxError"),
                                   (PYTHON_SOLUTION.replace("Hello, World!", "wrong"), "AssertionError")):
            with self.subTest(diagnostic=diagnostic):
                self.answer("python").write_text(source)
                result = self.cli("check", "python/hello", code=1)
                self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_rust_learner_compile_and_assertion_failures(self):
        for source, diagnostic in (("pub fn greeting() -> &'static str { 42 }\n", "mismatched types"),
                                   (RUST_SOLUTION.replace("Hello, World!", "wrong"), "assertion")):
            with self.subTest(diagnostic=diagnostic):
                self.answer("rust").write_text(source)
                result = self.cli("check", "rust/hello", code=1)
                self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_broken_python_harness_is_blocked(self):
        self.solve("python")
        harness = self.directory("python") / "test_exercises.py"
        for source in ("def broken(:\n", "raise RuntimeError('broken harness')\n"):
            with self.subTest(source=source):
                harness.write_text(source)
                self.cli("check", "python", code=2)

    def test_unknown_python_native_selector_is_blocked(self):
        self.solve("python")
        harness = self.directory("python") / "test_exercises.py"
        harness.write_text(harness.read_text().replace("def test_hello(", "def renamed_hello("))
        self.cli("check", "python/hello", code=2)

    def test_python_skips_cannot_report_success(self):
        self.solve("python")
        harness = self.directory("python") / "test_exercises.py"
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
        for filename in ("answers.py", "test_exercises.py"):
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
