"""Isolated Phase 3 integration tests; build with `cargo build --offline` first.

POLYGLOT_BIN may point to another built CLI. Only copied fixture answers are used.
"""

import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from git_fixture import isolated_git_env
from active_fixture import IDS, copy_active_fixture, exercise_path, solve


REPO = Path(__file__).resolve().parents[1]
TITLES = ("Hello, World!", "Find in String", "Length of Last Word",
          "Binary Search", "Fibonacci", "Hello, World!")
PYTHON_SOLUTION = '''def hello():
    print("Hello, World!")

def find_in_string(string, substring):
    return string.find(substring)

def length_of_last_word(text):
    words = text.split()
    return len(words[-1]) if words else 0
'''
RUST_SOLUTION = 'pub fn greeting() -> &\'static str { "Hello, World!" }\n'


class InteractiveCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = Path(os.environ.get("POLYGLOT_BIN", REPO / "target/debug/polyglot")).absolute()
        if not cls.binary.is_file() or not os.access(cls.binary, os.X_OK):
            raise RuntimeError(
                f"Rust CLI binary is missing or not executable: {cls.binary}. "
                f"Run `cargo build --offline` in {REPO}, or set POLYGLOT_BIN "
                "to an already-built Phase 3 executable."
            )
        cargo = shutil.which("cargo")
        if cargo is None:
            raise RuntimeError("Install Cargo and put it on PATH to run the Rust adapter tests.")
        # Preserve argv[0] for rustup's cargo dispatch rather than resolving it.
        cls.cargo = str(Path(cargo).absolute())
        cls.python = str(Path(sys.executable).absolute())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="polyglot interactive tests ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "copied repository with spaces"
        self.cwd = self.base / "unrelated working directory"
        self.env = isolated_git_env()
        self.cwd.mkdir()
        copy_active_fixture(self.root)
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.env["CARGO_TERM_COLOR"] = "never"
        for key in ("CARGO_TARGET_DIR", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS"):
            self.env.pop(key, None)
        shutil.copy2(REPO / ".gitignore", self.root / ".gitignore")
        for args in (("init", "--initial-branch=main"), ("add", "."),
                     ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "commit", "--no-gpg-sign", "-m", "Fixture"),
                     ("switch", "-c", "practice/fixture")):
            result = subprocess.run(["git", *args], cwd=self.root, env=self.env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def directory(self, language):
        return self.root / "practice" / language

    def answer(self, language, name="hello"):
        return exercise_path(self.root, language, name)

    def sources(self):
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if "target" not in path.relative_to(self.root).parts
            and ".git" not in path.relative_to(self.root).parts
            and path.is_file() and not path.is_symlink()
        }

    def command(self, *args, tools=True):
        missing = str(self.base / "missing executable")
        return [str(self.binary), "--root", str(self.root),
                "--python", self.python if tools else missing,
                "--cargo", self.cargo if tools else missing, *args]

    def cli(self, *args, input="", code=0, tools=True):
        result = subprocess.run(
            self.command(*args, tools=tools), input=input, text=True,
            capture_output=True, cwd=self.cwd,
            env=self.env, timeout=90,
        )
        self.assertEqual(result.returncode, code,
                         f"{result.args!r}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        return result.stdout + result.stderr

    def solve(self, language):
        solve(self.root, language)

    def selections(self, output):
        return re.findall(r"Exercise: ([a-z_/]+) \((\d+)/(\d+)\)", output)

    def assert_current(self, output, selection):
        matches = self.selections(output)
        self.assertTrue(matches, output)
        self.assertEqual(matches[-1][0], selection, output)

    def test_show_metadata_is_read_only_without_tools(self):
        before = self.sources()
        for selection, title in zip(IDS, TITLES):
            with self.subTest(selection=selection):
                output = self.cli("show", selection, tools=False)
                self.assertIn(f"Exercise: {selection}", output)
                self.assertIn(title, output)
                self.assertIn(f"Exercise file: {self.answer(*selection.split('/'))}", output)
                self.assertIn("Prompt:", output)
                self.assertNotIn("Hint:", output)
                if selection.endswith("hello"):
                    self.assertIn("Hello, World!", output)
                elif selection.endswith("find_in_string"):
                    self.assertIn("-1", output)
                    self.assertIn("0", output)
                else:
                    self.assertIn("0", output)
        self.assertEqual(self.sources(), before)

    def test_hint_is_read_only_without_tools(self):
        before = self.sources()
        for selection in IDS:
            with self.subTest(selection=selection):
                output = self.cli("hint", selection, tools=False)
                self.assertRegex(output, r"Hint:\s*\S")
        self.assertEqual(self.sources(), before)

    def test_malformed_ids_and_command_shapes_do_not_write(self):
        before = self.sources()
        for command in ("show", "hint", "practice"):
            for target in ("../python/hello", "python/../hello", "/python/hello",
                           "python/hello/", "python/nope", "go/hello", "", "hello"):
                with self.subTest(command=command, target=target):
                    self.cli(command, target, code=2, tools=False)
            self.cli(command, "python/hello", "extra", code=2, tools=False)
        for command in ("show", "hint"):
            for args in ((), ("python",), ("rust",)):
                self.cli(command, *args, code=2, tools=False)
        self.cli("practice", "python", "--python", self.python, code=2)
        self.assertEqual(self.sources(), before)

    def test_menu_quit_and_eof_never_prepare_answers(self):
        before = self.sources()
        for input in ("", "q\n", "quit\n", "invalid\nq\n", "\nquit\n"):
            with self.subTest(input=input):
                output = self.cli("practice", input=input, tools=False)
                self.assertIn("Choose a language", output)
                self.assertEqual(self.sources(), before)

    def test_menu_names_numbers_and_invalid_reprompt(self):
        before = self.sources()
        for selection, language in (("python", "python"), ("1", "python"),
                                    ("rust", "rust"), ("2", "rust")):
            with self.subTest(selection=selection):
                output = self.cli("practice", input=f"not a language\n{selection}\nq\n")
                self.assertGreaterEqual(output.count("Choose a language"), 2, output)
                self.assert_current(output, language + "/hello")
                self.assertEqual(self.sources(), before)

    def test_initial_selection_metadata_and_unchanged_exercise(self):
        before = self.sources()
        for index, selection in enumerate(IDS):
            language = selection.split("/")[0]
            with self.subTest(selection=selection):
                output = self.cli("practice", selection, input="q\n", tools=False)
                position, count = (index + 1, 5) if language == "python" else (1, 1)
                self.assertIn(f"Exercise: {selection} ({position}/{count})", output)
                self.assertIn(TITLES[index], output)
                self.assertIn(f"Exercise file: {self.answer(*selection.split('/'))}", output)
                self.assertIn("Prompt:", output)
                self.assertNotIn("Hint:", output)
                for command in ("check", "hint", "next", "previous", "list", "language", "quit"):
                    self.assertIn(command, output)
                self.assertNotIn("End of track", output)
                self.assertNotIn("all complete", output.lower())
                self.assertEqual(self.sources(), before)

    def test_existing_shared_answer_is_never_overwritten(self):
        for language in ("python", "rust"):
            self.solve(language)
        before = self.sources()
        for selection in IDS:
            self.cli("practice", selection, input="prompt\nq\n", tools=False)
        self.assertEqual(self.sources(), before)

    def test_check_aliases_use_current_python_selector_without_advancing(self):
        solve(self.root, "python", "hello")
        before = self.sources()
        output = self.cli("practice", "python/hello", input="\ncheck\nc\nprompt\nq\n")
        self.assertEqual(output.count("Passed"), 3, output)
        self.assertEqual(output.count("Ran 1 test"), 3, output)
        self.assertNotIn("Attempt failed", output)
        self.assert_current(output, "python/hello")
        self.assertNotIn("Exercise: python/find_in_string", output)
        self.assertEqual(self.sources(), before)

    def test_blank_next_is_gated_and_failed_checks_allow_clean_quit(self):
        output = self.cli("practice", "python", input="next\nn\ncheck\nprompt\nquit\n")
        self.assertEqual(output.count("Attempt failed"), 3, output)
        self.assert_current(output, "python/hello")
        self.assertNotIn("Exercise: python/find_in_string", output)
        self.assertNotIn("End of track", output)

    def test_solved_python_track_previous_boundaries_and_final_no_wrap(self):
        self.solve("python")
        before = self.sources()
        output = self.cli("practice", "python", input=(
            "previous\nprompt\nnext\nprompt\nn\nprompt\nnext\nprompt\nn\n"
            "next\nn\nprompt\np\nprompt\nprevious\nprevious\nprevious\nprevious\nprompt\nq\n"))
        self.assertEqual(output.count("Passed"), 6, output)
        self.assertGreaterEqual(output.count("End of track"), 2, output)
        positions = self.selections(output)
        for expected in ((selection, str(index), "5")
                         for index, selection in enumerate(IDS[:5], 1)):
            self.assertIn(expected, positions)
        self.assert_current(output, "python/hello")
        self.assertEqual(self.sources(), before)

    def test_solved_rust_check_next_and_single_exercise_boundaries(self):
        self.solve("rust")
        before = self.sources()
        output = self.cli("practice", "rust", input="p\nc\nnext\nn\nprompt\nq\n")
        self.assertEqual(output.count("Passed"), 3, output)
        self.assertEqual(output.count("test result:"), 3, output)
        self.assertGreaterEqual(output.count("End of track"), 2, output)
        self.assert_current(output, "rust/hello")
        self.assertEqual(self.sources(), before)

    def test_prompt_hint_help_and_list_aliases_are_read_only(self):
        self.solve("python")
        before = self.sources()
        output = self.cli("practice", "python/find_in_string",
                          input="hint\nh\nprompt\nhelp\n?\nlist\nl\nq\n", tools=False)
        self.assertEqual(output.count("Hint:"), 2, output)
        self.assertGreaterEqual(output.count("Prompt:"), 2, output)
        for selection in IDS[:5]:
            self.assertIn(selection, output)
        self.assertNotIn("rust/hello", output)
        self.assert_current(output, "python/find_in_string")
        self.assertEqual(self.sources(), before)

    def test_rust_list_contains_only_current_language(self):
        output = self.cli("practice", "rust", input="list\nl\nq\n", tools=False)
        rows = re.findall(r"(?:^|practice> )([a-z_/]+)\t", output, re.MULTILINE)
        self.assertEqual(rows, ["rust/hello", "rust/hello"])

    def test_language_switch_prepares_first_exercise_and_preserves_source(self):
        self.solve("python")
        rust_before = self.answer("rust").read_bytes()
        original = self.answer("python").read_bytes()
        output = self.cli("practice", "python/length_of_last_word",
                          input="language rust\nprompt\nlanguage python\nprompt\nq\n",
                          tools=False)
        self.assertIn("Exercise: rust/hello (1/1)", output)
        self.assert_current(output, "python/hello")
        self.assertEqual(self.answer("python").read_bytes(), original)
        self.assertEqual(self.answer("rust").read_bytes(), rust_before)

    def test_invalid_commands_and_language_recover_without_shell_or_writes(self):
        self.solve("python")
        before = self.sources()
        sentinel = self.cwd / "must not exist"
        for invalid in ("language go", "language", "language rust extra",
                        "nonsense", f'touch "{sentinel}"', "next extra"):
            with self.subTest(invalid=invalid):
                baseline = self.cli("practice", "python/find_in_string", input="q\n", tools=False)
                output = self.cli("practice", "python/find_in_string",
                                  input=f"{invalid}\nprompt\nq\n", tools=False)
                self.assert_current(output, "python/find_in_string")
                self.assertGreater(len(output), len(baseline), output)
                self.assertRegex(output.lower(), r"unknown|invalid|usage|unrecognized")
                self.assertEqual(self.sources(), before)
                self.assertFalse(sentinel.exists())

    def test_eof_after_selection_or_failed_check_is_clean(self):
        for input in ("", "check\n", "next\n", "hint\n"):
            with self.subTest(input=input):
                output = self.cli("practice", "python", input=input)
                self.assert_current(output, "python/hello")
                self.assertNotIn("Exercise: python/find_in_string", output)

    def test_blocked_check_keeps_session_usable(self):
        self.solve("python")
        before = self.sources()
        output = self.cli("practice", "python", tools=False,
                          input="check\nnext\nhint\nlist\nprompt\nq\n")
        self.assertIn("Blocked:", output)
        self.assertIn("Hint:", output)
        self.assert_current(output, "python/hello")
        self.assertNotIn("Exercise: python/find_in_string", output)
        self.assertEqual(self.sources(), before)

    def test_failed_destination_preparation_retains_current_selection(self):
        self.solve("python")
        self.answer("rust").unlink()
        before = self.sources()
        output = self.cli("practice", "python/find_in_string", tools=False,
                          input="language rust\nprompt\nhint\nq\n")
        self.assertIn("Blocked:", output)
        self.assert_current(output, "python/find_in_string")
        self.assertNotIn("Exercise: rust/hello", output)
        self.assertEqual(self.sources(), before)

    def test_failed_initial_preparation_is_blocked(self):
        for language in ("python", "rust"):
            with self.subTest(language=language):
                self.answer(language).unlink()
                before = self.sources()
                self.cli("practice", language, input="q\n", code=2, tools=False)
                self.assertEqual(self.sources(), before)

    def test_next_rechecks_after_equal_length_external_edit(self):
        self.solve("python")
        answer = self.answer("python")
        original = answer.read_bytes()
        changed = original.replace(b"Hello, World!", b"Wrong, World!")
        self.assertNotEqual(changed, original)
        self.assertEqual(len(changed), len(original))
        process = subprocess.Popen(
            self.command("practice", "python/hello"), cwd=self.cwd, env=self.env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        lines = queue.Queue()
        transcript = []

        def read_lines():
            try:
                for line in process.stdout:
                    lines.put(line)
            finally:
                lines.put(None)

        reader = threading.Thread(target=read_lines, daemon=True)
        reader.start()

        def wait_for(marker):
            deadline = time.monotonic() + 45
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self.fail(f"Timed out waiting for {marker!r}: {''.join(transcript)}")
                try:
                    line = lines.get(timeout=remaining)
                except queue.Empty:
                    self.fail(f"Timed out waiting for {marker!r}: {''.join(transcript)}")
                if line is None:
                    self.fail(f"CLI exited before {marker!r}: {''.join(transcript)}")
                transcript.append(line)
                if marker in line:
                    return

        try:
            process.stdin.write("check\n")
            process.stdin.flush()
            wait_for("Passed")
            timestamp = answer.stat().st_mtime_ns
            answer.write_bytes(changed)
            os.utime(answer, ns=(timestamp, timestamp))
            process.stdin.write("next\n")
            process.stdin.flush()
            wait_for("Attempt failed")
            process.stdin.write("prompt\nq\n")
            process.stdin.flush()
            process.stdin.close()
            self.assertEqual(process.wait(timeout=45), 0)
            reader.join(timeout=5)
            self.assertFalse(reader.is_alive(), "stdout reader did not finish")
            while not lines.empty():
                line = lines.get_nowait()
                if line is not None:
                    transcript.append(line)
            output = "".join(transcript)
            self.assert_current(output, "python/hello")
            self.assertNotIn("Exercise: python/find_in_string", output)
            self.assertEqual(output.count("Ran 1 test"), 2, output)
            self.assertEqual(answer.read_bytes(), changed)
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
