"""Integration checks using only disposable copies of the real practice fixtures."""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOLUTIONS = {
    "hello": '    print("Hello, World!")',
    "find_in_string": "    return string.find(substring)",
    "length_of_last_word": "    words = text.split()\n    return len(words[-1]) if words else 0",
}


class PolyglotCLITests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="polyglot cli ")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "repository with spaces"
        self.track = self.root / "practice" / "python"
        self.track.mkdir(parents=True)
        self.cwd = self.base / "unrelated cwd"
        self.cwd.mkdir()
        self.cli = self.root / "polyglot.py"
        shutil.copyfile(ROOT / "polyglot.py", self.cli)
        for name in ("starter.py", "test_exercises.py", "README.md"):
            shutil.copyfile(ROOT / "practice" / "python" / name, self.track / name)
        self.answers = self.track / "answers.py"

    def run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-B", str(self.cli), *args],
            cwd=self.cwd,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            text=True,
            capture_output=True,
            check=False,
        )
        return result

    def snapshot(self):
        return {
            str(path.relative_to(self.base)): path.read_bytes() if path.is_file() else None
            for path in self.base.rglob("*")
        }

    def solve(self, *exercises):
        source = (self.track / "starter.py").read_text()
        for exercise in exercises:
            source = source.replace(
                f'    raise NotImplementedError("Implement {exercise}")', SOLUTIONS[exercise]
            )
        self.answers.write_text(source)

    def test_listing_and_help_do_not_write(self):
        before = self.snapshot()
        for args in (("list",), ("list", "--language", "python")):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                for exercise in SOLUTIONS:
                    self.assertIn(f"python/{exercise}", result.stdout)
        for args in (("--help",), ("list", "--help"), ("start", "--help"), ("check", "--help")):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_input_does_not_write(self):
        before = self.snapshot()
        for args in (
            ("list", "--language", "rust"),
            ("start", "rust/hello"),
            ("check", "rust"),
            ("start", "python"),
            ("start", "python/missing"),
            ("check", "python/missing"),
            ("start", "../hello"),
        ):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)
                self.assertIn("python", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_start_creates_and_preserves_shared_attempt(self):
        result = self.run_cli("start", "python/hello")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.answers.read_bytes(), (self.track / "starter.py").read_bytes())
        self.assertIn(f"Created: {self.answers}", result.stdout)
        self.solve("hello")
        edited = self.answers.read_bytes()
        for exercise, title in (
            ("hello", "Hello World"),
            ("find_in_string", "Find in String"),
            ("length_of_last_word", "Length of Last Word"),
        ):
            with self.subTest(exercise=exercise):
                result = self.run_cli("start", f"python/{exercise}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Preserved: {self.answers}", result.stdout)
                self.assertIn(f"{title} ({exercise}())", result.stdout)
                self.assertIn(str(self.track / "README.md"), result.stdout)
                next_command = result.stdout.split("Next: ", 1)[1].strip()
                self.assertEqual(
                    shlex.split(next_command),
                    [sys.executable, str(self.cli), "check", f"python/{exercise}"],
                )
                self.assertEqual(self.answers.read_bytes(), edited)

    def test_rejects_directory_and_symlink_answers(self):
        outside = self.base / "outside.py"
        outside.write_text("untouched")
        for kind in ("directory", "symlink", "dangling symlink"):
            with self.subTest(kind=kind):
                if kind == "directory":
                    self.answers.mkdir()
                else:
                    self.answers.symlink_to(outside if kind == "symlink" else self.base / "absent")
                for command in ("start", "check"):
                    result = self.run_cli(command, "python/hello")
                    self.assertEqual(result.returncode, 2, result.stdout)
                    self.assertIn("move it aside", result.stderr)
                self.assertEqual(outside.read_text(), "untouched")
                if kind == "directory":
                    self.answers.rmdir()
                else:
                    self.answers.unlink()

    def test_missing_starter_does_not_create_answers(self):
        (self.track / "starter.py").unlink()
        result = self.run_cli("start", "python/hello")
        self.assertEqual(result.returncode, 2)
        self.assertIn("starter.py", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.answers.exists())

    def test_missing_answers_suggests_start_without_writes(self):
        before = self.snapshot()
        for target in ("python", "python/find_in_string"):
            result = self.run_cli("check", target)
            self.assertEqual(result.returncode, 2)
            self.assertIn("start python/", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_blank_attempt_fails_fast(self):
        self.assertEqual(self.run_cli("start", "python/hello").returncode, 0)
        for target in ("python/hello", "python"):
            result = self.run_cli("check", target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("NotImplementedError", result.stderr)
            self.assertIn("Ran 1 test", result.stderr)
        self.assertFalse(list(self.root.rglob("__pycache__")))

    def test_individual_checks_ignore_other_blank_exercises(self):
        for exercise in SOLUTIONS:
            with self.subTest(exercise=exercise):
                self.solve(exercise)
                result = self.run_cli("check", f"python/{exercise}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"test_{exercise} (test_exercises.PracticeTests", result.stderr)
                self.assertIn("Ran 1 test", result.stderr)

    def test_all_valid_answers_pass(self):
        self.solve(*SOLUTIONS)
        before = self.snapshot()
        result = self.run_cli("check", "python")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 3 tests", result.stderr)
        self.assertIn("OK", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_syntax_error_is_native_failure(self):
        self.answers.write_text("def hello(:\n")
        result = self.run_cli("check", "python/hello")
        self.assertEqual(result.returncode, 1)
        self.assertIn("SyntaxError", result.stderr)
        self.assertIn("answers.py", result.stderr)

    def test_import_has_no_side_effects(self):
        before = self.snapshot()
        result = subprocess.run(
            [sys.executable, "-B", "-c", (
                "import runpy; "
                f"runpy.run_path({str(self.cli)!r}, run_name='imported_polyglot')"
            )],
            cwd=self.cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout + result.stderr, "")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
