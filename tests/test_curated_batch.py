"""Ten published examples checked only as copied, disposable learner inputs."""

import ast
import json
import re
import subprocess
import unittest

from active_fixture import EXAMPLE_PATHS, IDS, NAMES, QUESTIONS, REPO, RUST_SOLUTIONS, SOLUTIONS, solve
import test_rust_cli as cli_fixture


TERMS = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610,
         987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025,
         121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578,
         5702887, 9227465, 14930352, 24157817, 39088169, 63245986, 102334155]
RUST_HEADERS = {
    "hello": "pub fn greeting() -> &'static str",
    "find_in_string": "pub fn find_in_string(string: &str, substring: &str) -> isize",
    "length_of_last_word": "pub fn length_of_last_word(text: &str) -> usize",
    "binary_search": "pub fn binary_search(target: i32, arr: &[i32]) -> bool",
    "fibonacci": "pub fn fibonacci(length: usize) -> Vec<u32>",
}


def rust_harness(root, name):
    return root / "practice/rust" / ("checks.rs" if name == "hello" else f"tests/{name}.rs")


class CuratedBatchTests(unittest.TestCase):
    # Reuse fixture mechanics without inheriting and rerunning the older test suite.
    setUpClass = classmethod(cli_fixture.RustCliTests.setUpClass.__func__)
    setUp = cli_fixture.RustCliTests.setUp
    directory = cli_fixture.RustCliTests.directory
    answer = cli_fixture.RustCliTests.answer
    sources = cli_fixture.RustCliTests.sources
    git_files = cli_fixture.RustCliTests.git_files
    execute = cli_fixture.RustCliTests.execute
    assert_code = cli_fixture.RustCliTests.assert_code
    cli = cli_fixture.RustCliTests.cli
    native = cli_fixture.RustCliTests.native

    def test_all_ten_published_examples_pass_selected_native_checks_with_siblings_blank(self):
        for selection in IDS:
            language, name = selection.split("/")
            with self.subTest(selection=selection):
                path = self.answer(language, name)
                blank = path.read_bytes()
                self.cli("check", selection, code=1)
                solve(self.root, language, name)
                self.assertEqual(path.read_text(), EXAMPLE_PATHS[language][name].read_text())
                self.cli("check", selection)
                if language == "rust":
                    self.assert_code(self.native(language, name), 0)
                self.cli("check", language, code=1)
                path.write_bytes(blank)

    def test_published_examples_have_only_definitions_and_no_demo_entrypoints(self):
        self.assertEqual(sum(map(len, EXAMPLE_PATHS.values())), 10)
        for language, paths in EXAMPLE_PATHS.items():
            self.assertEqual(set(paths), set(NAMES))
            for name, path in paths.items():
                with self.subTest(path=path):
                    source = path.read_text()
                    self.assertTrue(source.strip())
                    if language == "python":
                        tree = ast.parse(source)
                        for node in tree.body:
                            self.assertTrue(isinstance(node, (ast.FunctionDef, ast.Import, ast.ImportFrom))
                                            or (isinstance(node, ast.Expr)
                                                and isinstance(node.value, ast.Constant)
                                                and isinstance(node.value.value, str)), ast.dump(node))
                        self.assertIn(name, [node.name for node in tree.body
                                            if isinstance(node, ast.FunctionDef)])
                    else:
                        self.assertRegex(source, r"pub fn " + ("greeting" if name == "hello" else name) + r"\s*\(")
                        self.assertNotRegex(source, r"\bfn\s+main\s*\(|\b(?:print|println|dbg)!|todo!")

    def test_five_shared_questions_bind_both_languages_and_checked_examples(self):
        rows = json.loads(self.cli("questions").stdout)
        curated = {row["id"]: row for row in rows if row["question_status"] == "curated"}
        self.assertEqual(set(curated), set(QUESTIONS))
        for topic, name in zip(QUESTIONS, NAMES):
            row = curated[topic]
            self.assertEqual(row["bindings"], [f"python/{name}", f"rust/{name}"])
            for language in ("python", "rust"):
                path = str(EXAMPLE_PATHS[language][name].relative_to(REPO))
                ref = next(ref for ref in row["references"] if ref["path"] == path)
                self.assertRegex(ref["note"].lower(), r"checked.*native|native.*checked")

    def test_each_rust_target_ignores_all_broken_or_missing_sibling_sources_and_harnesses(self):
        originals = {path: path.read_bytes() for name in NAMES
                     for path in (self.answer("rust", name), rust_harness(self.root, name))}
        for selected in NAMES:
            for damage in ("source syntax", "source missing", "harness syntax", "harness missing"):
                with self.subTest(selected=selected, damage=damage):
                    for path, content in originals.items():
                        path.write_bytes(content)
                    solve(self.root, "rust", selected)
                    for sibling in NAMES:
                        if sibling == selected:
                            continue
                        path = (rust_harness(self.root, sibling) if damage.startswith("harness")
                                else self.answer("rust", sibling))
                        if damage.endswith("missing"):
                            path.unlink()
                        else:
                            path.write_text("this is not Rust;\n")
                    before, metadata = self.sources(), self.git_files()
                    self.cli("start", "rust/" + selected)
                    self.cli("check", "rust/" + selected)
                    self.cli("practice", "rust/" + selected)
                    self.assert_code(self.native("rust", selected), 0)
                    self.assertEqual(self.sources(), before)
                    self.assertEqual(self.git_files(), metadata)

    def test_rust_nested_diagnostics_distinguish_learner_errors_from_harness_errors(self):
        for name in NAMES:
            path = self.answer("rust", name)
            for body in ("let broken = ;", "return (); "):
                with self.subTest(name=name, body=body):
                    path.write_text(RUST_HEADERS[name] + " { " + body + " }\n")
                    result = self.cli("check", "rust/" + name, code=1)
                    self.assertIn("error", result.stdout + result.stderr)
                    if name != "hello":
                        self.assertIn("../exercises/", result.stdout + result.stderr)
            solve(self.root, "rust", name)
            harness = rust_harness(self.root, name)
            original = harness.read_bytes()
            harness.write_text("fn broken( {\n")
            self.cli("check", "rust/" + name, code=2)
            harness.write_bytes(original)

    def test_all_rust_targets_reject_zero_and_ignored_selected_tests(self):
        solve(self.root, "rust")
        for name in NAMES:
            harness = rust_harness(self.root, name)
            original = harness.read_text()
            for source, code in ((re.sub(r"fn " + name + r"\(", "fn renamed(", original), 2),
                                 (original.replace("#[test]", "#[test]\n#[ignore]"), 3)):
                with self.subTest(name=name, code=code):
                    self.assertNotEqual(source, original)
                    harness.write_text(source)
                    self.cli("check", "rust/" + name, code=code)
            harness.write_text(original)

    def test_whole_rust_track_requires_every_selected_check_to_pass(self):
        blanks = {name: self.answer("rust", name).read_bytes() for name in NAMES}
        solve(self.root, "rust")
        self.cli("check", "rust")
        self.assert_code(self.native("rust"), 0)
        for name in NAMES:
            with self.subTest(name=name):
                self.answer("rust", name).write_bytes(blanks[name])
                self.cli("check", "rust", code=1)
                solve(self.root, "rust", name)

    def test_rust_native_contract_rejects_semantic_mutants(self):
        cases = {
            "hello": ['"wrong"'],
            "find_in_string": ["0", "string.rfind(substring).map_or(-1, |i| i as isize)",
                               "string.to_lowercase().find(&substring.to_lowercase()).map_or(-1, |i| i as isize)",
                               "string.find(substring).map_or(0, |i| i as isize)"],
            "length_of_last_word": ["0", "text.split(' ').last().unwrap_or(\"\").len()",
                                    "text.split_ascii_whitespace().last().unwrap_or(\"\").len()",
                                    "text.split_ascii_whitespace().last().unwrap_or(\"\").trim_matches(|c: char| !c.is_alphabetic()).len()"],
            "binary_search": ["false", "arr.len() > 2 && arr[1..arr.len()-1].contains(&target)",
                              "arr.windows(2).all(|p| p[0] != p[1]) && arr.contains(&target)"],
            "fibonacci": ["vec![1; length]", "vec![0, 1].into_iter().take(length).collect()",
                          "{ let mut v = vec![]; let (mut a, mut b) = (1, 1); while v.len() < length { v.push(a); v.push(b); a += b; b += a; } v }"],
        }
        for name, bodies in cases.items():
            for body in bodies:
                with self.subTest(name=name, body=body):
                    self.answer("rust", name).write_text(RUST_HEADERS[name] + " { " + body + " }\n")
                    self.cli("check", "rust/" + name, code=1)

    def test_rust_native_checks_reject_wrong_api_signatures_and_gate_next(self):
        cases = {
            "hello": 'pub fn greeting() -> String { "Hello, World!".to_owned() }',
            "find_in_string": 'pub fn find_in_string(string: &str, substring: &str) -> i32 { string.find(substring).map_or(-1, |i| i as i32) }',
            "length_of_last_word": 'pub fn length_of_last_word(text: &str) -> u8 { text.split_whitespace().next_back().map_or(0, |word| word.len() as u8) }',
            "binary_search": 'pub fn binary_search(target: i64, arr: &[i64]) -> bool { arr.contains(&target) }',
            "fibonacci": 'pub fn fibonacci(length: usize) -> Vec<u64> { let (mut a, mut b) = (1, 1); (0..length).map(|_| { let result = a; (a, b) = (b, a + b); result }).collect() }',
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.answer("rust", name).write_text(source + "\n")
                result = self.cli("check", "rust/" + name, code=1)
                self.assertIn("E0308", result.stdout + result.stderr)
                session = subprocess.run(
                    [str(self.binary), "--root", str(self.root), "--python", self.python,
                     "--cargo", self.cargo, "practice", "rust/" + name],
                    cwd=self.cwd, env=self.env, input="check\nnext\nq\n",
                    capture_output=True, text=True, timeout=90,
                )
                self.assert_code(session, 0)
                output = session.stdout + session.stderr
                self.assertEqual(output.count("Attempt failed"), 2, output)
                self.assertNotIn("End of track", output)
                next_index = NAMES.index(name) + 1
                if next_index < len(NAMES):
                    self.assertNotIn("Exercise: rust/" + NAMES[next_index], output)

    def test_rust_examples_against_independent_fixed_contract_cases(self):
        cases = {
            "hello": 'let greeting: fn() -> &\'static str = exercise::greeting; assert_eq!(greeting(), "Hello, World!");',
            "find_in_string": '''
                let find: fn(&str, &str) -> isize = exercise::find_in_string;
                for (text, needle, expected) in [("", "", 0), ("", "x", -1),
                    ("abcabc", "abc", 0), ("AbC", "abc", -1), ("abc", "", 0),
                    ("hello world", "world", 6), ("ab", "abc", -1)] {
                    assert_eq!(find(text, needle), expected);
                }
                assert_eq!(find(&"a".repeat(300), "b"), -1);
                assert_eq!(find(&("a".repeat(299) + "b"), "b"), 299);
            ''',
            "length_of_last_word": '''
                let last_word: fn(&str) -> usize = exercise::length_of_last_word;
                for (text, expected) in [("", 0), (" \\t\\n\\r", 0), ("hello world", 5),
                    ("hello\\tworld\\n", 5), ("hello\\x0bworld\\x0c", 5),
                    ("a word!  ", 5), ("...", 3)] {
                    assert_eq!(last_word(text), expected);
                }
                assert_eq!(last_word(&"x".repeat(300)), 300);
            ''',
            "binary_search": '''
                let search: fn(i32, &[i32]) -> bool = exercise::binary_search;
                for (arr, target, expected) in [(&[][..], 0, false), (&[-9, -3, 0, 4][..], -9, true),
                    (&[-9, -3, 0, 4][..], 4, true), (&[-9, -3, 0, 4][..], -4, false),
                    (&[2, 2, 2][..], 2, true), (&[i32::MIN, 0, i32::MAX][..], i32::MIN, true),
                    (&[i32::MIN, 0, i32::MAX][..], i32::MAX, true)] {
                    let before = arr.to_vec();
                    let actual: bool = search(target, arr);
                    assert_eq!(actual, expected); assert_eq!(arr, before);
                }
            ''',
            "fibonacci": f'''
                let fibonacci: fn(usize) -> Vec<u32> = exercise::fibonacci;
                let terms: Vec<u32> = vec!{TERMS!r};
                for length in 0..=40 {{
                    assert_eq!(fibonacci(length), terms[..length]);
                }}
            ''',
        }
        solve(self.root, "rust")
        for name, body in cases.items():
            with self.subTest(name=name):
                harness = rust_harness(self.root, name)
                with harness.open("a") as stream:
                    stream.write("\n#[test]\nfn independent_contract() {\n" + body + "\n}\n")
                self.assert_code(self.native("rust", name), 0)

    def test_missing_or_private_rust_functions_are_learner_api_errors(self):
        for name, solution in RUST_SOLUTIONS.items():
            function = "greeting" if name == "hello" else name
            for source, diagnostic in (
                (solution.replace(f"fn {function}(", f"fn renamed_{function}("), "E0425"),
                (solution.replace("pub fn ", "fn ", 1), "E0603"),
            ):
                with self.subTest(name=name, diagnostic=diagnostic):
                    self.answer("rust", name).write_text(source)
                    result = self.cli("check", "rust/" + name, code=1)
                    self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_python_examples_against_independent_fixed_contract_cases(self):
        solve(self.root, "python")
        harness = self.directory("python") / "tests/test_batch_oracle.py"
        harness.write_text('''import contextlib
import io
import unittest
from exercises.hello import hello
from exercises.find_in_string import find_in_string
from exercises.length_of_last_word import length_of_last_word
from exercises.binary_search import binary_search
from exercises.fibonacci import fibonacci

class IndependentContracts(unittest.TestCase):
    def test_contracts(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertIsNone(hello())
        self.assertEqual(output.getvalue(), "Hello, World!\\n")
        for text, needle, expected in [("", "", 0), ("", "x", -1),
                ("abcabc", "abc", 0), ("AbC", "abc", -1), ("abc", "", 0),
                ("ab", "abc", -1), ("a" * 300, "b", -1), ("a" * 300 + "b", "b", 300)]:
            result = find_in_string(text, needle)
            self.assertIs(type(result), int)
            self.assertEqual(result, expected)
        for text, expected in [("", 0), (" \\t\\n\\r", 0), ("hello world", 5),
                ("hello\\tworld\\n", 5), ("hello\\vworld\\f", 5),
                ("a word!  ", 5), ("...", 3), ("x" * 300, 300)]:
            result = length_of_last_word(text)
            self.assertIs(type(result), int)
            self.assertEqual(result, expected)
        for arr, target, expected in [([], 0, False), ([-9, -3, 0, 4], -9, True),
                ([-9, -3, 0, 4], 4, True), ([-9, -3, 0, 4], -4, False), ([2, 2, 2], 2, True),
                ([-2147483648, 0, 2147483647], -2147483648, True),
                ([-2147483648, 0, 2147483647], 2147483647, True)]:
            before = arr.copy()
            result = binary_search(target, arr)
            self.assertIs(type(result), bool)
            self.assertEqual(result, expected)
            self.assertEqual(arr, before)
        for length in range(41):
            result = fibonacci(length)
            self.assertIs(type(result), list)
            self.assertTrue(all(type(term) is int for term in result))
            self.assertEqual(result, TERMS[:length])
''' + f"\nTERMS = {TERMS!r}\n")
        self.assert_code(self.native("python"), 0)

    def test_python_native_checks_reject_wrong_return_types_for_every_binding(self):
        for name, body in {
            "hello": 'print("Hello, World!"); return "Hello, World!"',
            "find_in_string": "return False",
            "length_of_last_word": "return False",
            "binary_search": "return int(target in arr)",
            "fibonacci": "return tuple([1] * length)",
        }.items():
            with self.subTest(name=name):
                self.answer("python", name).write_text(
                    SOLUTIONS[name].splitlines()[0] + "\n    " + body + "\n")
                self.cli("check", "python/" + name, code=1)


if __name__ == "__main__":
    unittest.main()
