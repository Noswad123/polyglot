"""Shared question contracts and native bindings in disposable repositories only."""

import ast
import json
import shutil
import subprocess
import unittest

from active_fixture import IDS, PAIRED_IDS, LANGUAGES, QUESTIONS, SOLUTIONS, exercise_path, solve
from test_branch_policy import BranchFixture


class QuestionLibraryTests(BranchFixture, unittest.TestCase):
    def question_path(self, problem="hello-world"):
        return self.root / "README/katas" / QUESTIONS[problem]

    def test_registered_questions_and_full_docs_need_no_git_or_tools(self):
        shutil.rmtree(self.root / ".git")
        shutil.rmtree(self.root / "practice")
        (self.root / "README/katas/boggle.md").write_text("# Unregistered draft\n")
        env = {**self.env, "PATH": ""}
        before = self.sources()
        inventory = json.loads(self.cli("questions", env=env))
        self.assertEqual(inventory, json.loads(self.cli("questions", "--json", env=env)))
        self.assertEqual({item["id"] for item in inventory if item["question_status"] == "curated"},
                         set(QUESTIONS))
        self.assertEqual(len(inventory), 37)
        for problem, filename in QUESTIONS.items():
            with self.subTest(problem=problem):
                document = self.question_path(problem).read_text().strip()
                self.assertTrue(document)
                output = self.cli("question", problem, env=env)
                self.assertIn(document, output)
                self.assertIn(str(self.question_path(problem)), output)
                self.assertIn(filename, output)
        for selection in IDS:
            self.cli("show", selection, env=env)
        self.assertEqual(self.sources(), before)
        self.assertFalse((self.root / ".git").exists())

    def test_hello_shared_contract_has_explicit_different_native_bindings(self):
        document = self.question_path().read_text().strip()
        selections = [language + "/hello" for language in LANGUAGES]
        outputs = [self.cli("show", selection) for selection in selections]
        for output, selection in zip(outputs, selections):
            self.assertIn(f"Exercise: {selection}", output)
            self.assertIn("Title:", output)
            self.assertIn("Problem: hello-world", output)
            self.assertIn(f"Question file: {self.question_path()}", output)
            self.assertIn("Prompt:", output)
            self.assertIn(document, output)
            self.assertIn("Language task:", output)
            self.assertNotIn("Hint:", output)
        self.assertIn("hello() -> None", outputs[0].split("Language task:", 1)[1])
        self.assertIn("greeting() -> &'static str", outputs[1].split("Language task:", 1)[1])
        for output, signature in zip(outputs[2:], ("hello(): void", "func Hello() string",
                                                   "hello shell function", "global function hello()")):
            self.assertIn(signature, output.split("Language task:", 1)[1])
        rows = {line.split("|")[1].strip().strip("`"): line.lower()
                for line in document.splitlines() if line.startswith("| `")}
        self.assertEqual(set(rows), set(selections))
        for language in LANGUAGES:
            row = rows[language + "/hello"]
            self.assertIn("return" if language in ("rust", "go") else "print", row)
            self.assertIn("newline", row)
        self.assertIn("print", document.lower())
        self.assertIn("return", document.lower())
        library = json.loads(self.cli("questions"))
        hello = next(problem for problem in library if problem["id"] == "hello-world")
        self.assertEqual(hello["title"], "Hello, World!")
        self.assertEqual(hello["bindings"], [language + "/hello" for language in LANGUAGES])

    def test_every_binding_shows_its_registered_question_and_signature(self):
        problems = tuple(QUESTIONS) * 2
        signatures = ("hello() -> None", "find_in_string(string: str, substring: str) -> int",
                      "length_of_last_word(text: str) -> int",
                      "binary_search(target: int, arr: list[int]) -> bool",
                      "fibonacci(length: int) -> list[int]", "greeting() -> &'static str",
                      "find_in_string(string: &str, substring: &str) -> isize",
                      "length_of_last_word(text: &str) -> usize",
                      "binary_search(target: i32, arr: &[i32]) -> bool",
                      "fibonacci(length: usize) -> Vec<u32>")
        self.assertEqual(len(signatures), len(PAIRED_IDS))
        for selection, problem, signature in zip(PAIRED_IDS, problems, signatures):
            with self.subTest(selection=selection):
                output = self.cli("show", selection)
                self.assertIn(f"Problem: {problem}", output)
                self.assertIn(f"Question file: {self.question_path(problem)}", output)
                self.assertIn(self.question_path(problem).read_text().strip(), output)
                self.assertIn(f"Exercise file: {exercise_path(self.root, *selection.split('/'))}", output)
                self.assertIn("Language task:", output)
                self.assertIn(signature, output.split("Language task:", 1)[1])

    def test_document_edits_are_read_at_runtime_in_show_question_and_session(self):
        self.git("switch", "-c", "practice/docs")
        path = self.question_path()
        path.write_text(path.read_text() + "\nRuntime-only contract marker 72913.\n")
        before, metadata = self.sources(), self.git_files()
        for args in (("question", "hello-world"), ("show", "python/hello"),
                     ("show", "rust/hello"), ("practice", "python/hello")):
            output = self.cli(*args, input="prompt\nq\n")
            self.assertIn(path.read_text().strip(), output)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_missing_empty_and_symlink_questions_block_before_autobranch(self):
        path = self.question_path()
        original = path.read_bytes()
        outside = self.base / "outside question.md"
        outside.write_bytes(original)
        for kind in ("missing", "empty", "whitespace", "symlink", "directory"):
            with self.subTest(kind=kind):
                path.unlink()
                if kind == "empty":
                    path.write_bytes(b"")
                elif kind == "whitespace":
                    path.write_text(" \n\t\n")
                elif kind == "symlink":
                    path.symlink_to(outside)
                elif kind == "directory":
                    path.mkdir()
                # Commit the invalid doc so dirty-main protection cannot mask validation.
                self.git("add", "-A")
                self.commit()
                for command in ("question", "show", "start", "practice"):
                    target = "hello-world" if command == "question" else "python/hello"
                    output = self.assert_blocked(command, target)
                    self.assertIn("Blocked:", output)
                    self.assertIn(str(path), output)
                self.assertEqual(self.git("branch", "--show-current"), "main")
                self.assertEqual(outside.read_bytes(), original)
                if path.is_dir() and not path.is_symlink():
                    path.rmdir()
                elif path.exists() or path.is_symlink():
                    path.unlink()
                path.write_bytes(original)

    def test_question_parent_symlinks_are_rejected(self):
        for relative in ("README/katas", "README"):
            with self.subTest(relative=relative):
                path = self.root / relative
                outside = self.base / relative.replace("/", "-")
                path.rename(outside)
                path.symlink_to(outside, target_is_directory=True)
                try:
                    for args in (("question", "hello-world"), ("show", "python/hello"),
                                 ("practice", "python/hello")):
                        self.assert_blocked(*args)
                finally:
                    path.unlink()
                    outside.rename(path)

    def test_list_questions_hint_and_check_do_not_read_docs(self):
        solve(self.root, "python")
        shutil.rmtree(self.root / "README")
        before, metadata = self.sources(), self.git_files()
        env = {**self.env, "PATH": ""}
        for args in (("list",), ("questions",), *(("hint", item) for item in IDS),
                     ("check", "python"), *(("check", item) for item in IDS[:5])):
            self.cli(*args, env=env)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)
        shutil.rmtree(self.root / "practice")
        before = self.sources()
        for args in (("list",), ("questions",), ("hint", "python/binary_search")):
            self.cli(*args, env=env)
        self.assertEqual(self.sources(), before)

    def test_question_argument_shapes_and_unknown_topics_do_not_write(self):
        before, metadata = self.sources(), self.git_files()
        for args in (("questions", "extra"), ("questions", "--language", "python"),
                     ("question",), ("question", "hello-world", "extra")):
            self.cli(*args, code=2)
        for problem in ("", "hello", "python/hello", "../hello-world", "/hello-world",
                        "hello-world/", "HELLO-WORLD", "rotateArray", "nonexistent-topic", "nope"):
            with self.subTest(problem=problem):
                self.cli("question", problem, code=2)
        self.assertIn("draft", self.cli("question", "boggle").lower())
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_native_hints_are_distinct_and_only_requested_explicitly(self):
        hints = [self.cli("hint", selection).split("Hint:", 1)[1].strip()
                 for selection in ("python/hello", "rust/hello")]
        self.assertNotEqual(*hints)
        self.assertTrue(all(hints))
        for hint in hints:
            self.assertNotIn(hint, self.cli("question", "hello-world"))
            self.assertNotIn(hint, self.cli("show", "python/hello"))
            self.assertNotIn(hint, self.cli("show", "rust/hello"))

    def test_new_python_starters_are_only_not_implemented(self):
        for name in ("binary_search", "fibonacci"):
            with self.subTest(name=name):
                tree = ast.parse(exercise_path(self.root, "python", name).read_text())
                function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
                self.assertEqual(function.name, name)
                body = function.body
                if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                    body = body[1:]
                self.assertEqual(len(body), 1)
                self.assertIsInstance(body[0], ast.Raise)
                raised = body[0].exc
                self.assertEqual((raised.func if isinstance(raised, ast.Call) else raised).id,
                                 "NotImplementedError")
                self.cli("check", "python/" + name, code=1)
                solve(self.root, "python", name)
                self.cli("check", "python/" + name)

    def test_new_native_checks_reject_wrong_contracts_with_clear_feedback(self):
        # README/katas/binarySearch.md: ascending, read-only membership; strict bool, not index.
        # README/katas/fibonacci.md: exactly N terms, 1, 1 prefix, core range 0..40.
        cases = (
            ("binary_search", "return arr.index(target) if target in arr else -1"),
            ("binary_search", "return int(target in arr)"),
            ("binary_search", "present = target in arr; arr.clear(); return present"),
            ("binary_search", "return False"),
            ("binary_search", "return target in arr[1:-1]"),
            ("binary_search", "return target in arr if len(set(arr)) == len(arr) else False"),
            ("fibonacci", "return [0, 1][:length]"),
            ("fibonacci", "return [1] * length"),
            ("fibonacci", "return tuple([1] * length)"),
        )
        for name, body in cases:
            with self.subTest(name=name, body=body):
                signature = SOLUTIONS[name].splitlines()[0]
                exercise_path(self.root, "python", name).write_text(signature + "\n    " + body + "\n")
                output = self.cli("check", "python/" + name, code=1)
                self.assertIn("Your ", output)
                self.assertIn("Expected ", output)

    def test_new_selected_checks_ignore_broken_sibling_sources_and_harnesses(self):
        solve(self.root, "python")
        exercise_path(self.root, "python", "hello").write_text("def broken(:\n")
        (self.root / "practice/python/tests/test_hello.py").write_text("def broken(:\n")
        before, metadata = self.sources(), self.git_files()
        for name in ("binary_search", "fibonacci"):
            with self.subTest(name=name):
                self.cli("check", "python/" + name)
        self.assertEqual(self.sources(), before)
        self.assertEqual(self.git_files(), metadata)

    def test_fibonacci_solution_matches_every_core_length_independent_oracle(self):
        # Fixed terms avoid using the fixture solution's recurrence as the oracle.
        terms = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610,
                 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368,
                 75025, 121393, 196418, 317811, 514229, 832040, 1346269,
                 2178309, 3524578, 5702887, 9227465, 14930352, 24157817,
                 39088169, 63245986, 102334155]
        solve(self.root, "python", "fibonacci")
        result = subprocess.run(
            [self.python, "-B", "-c", "import json; from exercises.fibonacci import fibonacci; "
             "print(json.dumps([fibonacci(n) for n in range(41)]))"],
            cwd=self.root / "practice/python", env=self.env,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = json.loads(result.stdout)
        self.assertEqual(len(actual), 41)
        for length in range(41):
            with self.subTest(length=length):
                self.assertEqual(actual[length], terms[:length])

    def test_native_fibonacci_rejects_pair_appending_overshoot(self):
        # This implementation satisfies the old even-length sample cases but
        # overshoots every odd requested length above one.
        exercise_path(self.root, "python", "fibonacci").write_text(
            "def fibonacci(length):\n"
            "    if length < 2:\n"
            "        return [1][:length]\n"
            "    values = [1, 1]\n"
            "    while len(values) < length:\n"
            "        values.append(values[-1] + values[-2])\n"
            "        values.append(values[-1] + values[-2])\n"
            "    return values\n"
        )
        output = self.cli("check", "python/fibonacci", code=1)
        self.assertIn("length=3", output)
        self.assertIn("Your result:", output)
        self.assertIn("Expected result:", output)

    def test_failed_question_navigation_retains_current_index(self):
        self.git("switch", "-c", "practice/navigation")
        solve(self.root, "python")
        cases = (
            ("python/length_of_last_word", "length-of-last-word", "binary-search", "next", "python/binary_search", 3),
            ("python/binary_search", "binary-search", "length-of-last-word", "previous", "python/length_of_last_word", 4),
            ("python/fibonacci", "fibonacci", "hello-world", "language rust", "rust/hello", 5),
        )
        for current, problem, missing, action, target, position in cases:
            with self.subTest(action=action):
                document = self.question_path(missing)
                original = document.read_bytes()
                document.unlink()
                try:
                    before, metadata = self.sources(), self.git_files()
                    output = self.cli("practice", current, input=f"{action}\nprompt\nhint\nq\n")
                    self.assertIn("Blocked:", output)
                    self.assertIn(f"Exercise: {current} ({position}/5)", output)
                    self.assertNotIn(f"Exercise: {target}", output)
                    self.assertIn(self.question_path(problem).read_text().strip(), output)
                    self.assertEqual(self.sources(), before)
                    self.assertEqual(self.git_files(), metadata)
                finally:
                    document.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
