"""Independent collection audit; legacy source files are never imported or run."""

from collections import Counter
import json
import os
import re
import shutil
import subprocess
import unittest

from active_fixture import IDS, QUESTIONS, REPO
from test_branch_policy import BranchFixture


MISSING = {
    "best-time-to-buy-and-sell-stock", "candy", "container-with-most-water",
    "find-pivot-index", "gas-station", "h-index", "insert-delete-get-random",
    "jump-game", "longest-common-prefix", "queue", "remove-duplicates-from-sorted-array",
    "remove-element", "stack", "text-justification", "trapping-rain-water", "two-sum",
    "zigzag-conversion",
}
DRAFTS = {
    "boggle", "integer-to-roman", "is-subsequence", "majority-element",
    "merge-sorted-array", "pong", "product-of-array-except-self",
    "reverse-words-in-a-string", "roman-to-integer", "rotate-array", "scrabble",
    "spiral-matrix", "sudoku-validator", "users", "valid-palindrome",
}
SUFFIXES = {"python": ".py", "typescript": ".ts", "javascript": ".js", "go": ".go",
            "rust": ".rs", "bash": ".sh", "lua": ".lua", "lisp": ".lisp"}
IMPLEMENTATION_ROOTS = {
    "python": "practice/python/soutions",
    "typescript": "practice/typescript",
    "javascript": "practice/javascript",
    "go": "practice/go",
    "rust": "practice/rust/solutions",
    "bash": "practice/bash",
    "lua": "practice/lua",
    "lisp": "practice/lisp",
}


def source_topic(path):
    # Filename aliases, not the production inventory, define the audit oracle.
    stem = path.stem
    if stem == "main":
        stem = path.parent.parent.name if path.parent.name == "src" else path.parent.name
    aliases = {"roateArray": "rotate-array",
               "findTheIndexOfTheFirstOccurrenceInAString": "find-in-string",
               "strStr": "find-in-string"}
    words = re.sub(r"([A-Z])([A-Z][a-z])", r"\1-\2", stem)
    return aliases.get(stem, re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", words).replace("_", "-").lower())


class LibraryInventoryTests(BranchFixture, unittest.TestCase):
    def inventory(self, env=None, *, arguments=("--json",)):
        result = subprocess.run(self.command("questions", *arguments), cwd=self.base,
                                env=env or self.env, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "", "JSON mode must not emit diagnostics on success")
        rows = json.loads(result.stdout)
        self.assertIsInstance(rows, list)
        self.assertEqual(len(rows), 37)
        self.assertEqual(len({row["id"] for row in rows}), 37)
        for row in rows:
            self.assertEqual(set(row), {"id", "title", "question_status", "question_doc",
                                        "references", "bindings"})
            for field in ("id", "title", "question_status"):
                self.assertIsInstance(row[field], str)
                self.assertTrue(row[field])
            self.assertTrue(row["question_doc"] is None or isinstance(row["question_doc"], str))
            self.assertIsInstance(row["references"], list)
            self.assertIsInstance(row["bindings"], list)
            self.assertTrue(all(isinstance(item, str) for item in row["bindings"]))
            for reference in row["references"]:
                self.assertEqual(set(reference), {"language", "path", "note"})
                self.assertIsInstance(reference["language"], str)
                self.assertIsInstance(reference["path"], str)
                self.assertTrue(reference["note"] is None or isinstance(reference["note"], str))
        return {row["id"]: row for row in rows}

    def test_independent_inventory_matches_all_docs_and_solution_artifacts(self):
        rows = self.inventory()
        self.assertEqual(set(rows), set(QUESTIONS) | DRAFTS | MISSING)
        self.assertEqual(Counter(row["question_status"] for row in rows.values()),
                         {"curated": 5, "draft": 15, "missing": 17})
        for status, topics in (("curated", set(QUESTIONS)), ("draft", DRAFTS), ("missing", MISSING)):
            self.assertEqual({key for key, row in rows.items() if row["question_status"] == status}, topics)
        docs = [row["question_doc"] for row in rows.values() if row["question_doc"] is not None]
        actual_docs = {str(path.relative_to(REPO)) for path in (REPO / "README/katas").glob("*.md")
                       if path.name != "index.md"}
        self.assertEqual(len(docs), 20)
        self.assertEqual(set(docs), actual_docs)
        self.assertTrue(all((self.root / path).is_file() for path in docs))
        self.assertTrue(all(rows[topic]["question_doc"] is None for topic in MISSING))
        refs = [ref for row in rows.values() for ref in row["references"]]
        self.assertEqual(len(refs), 70)
        self.assertEqual(len({ref["path"] for ref in refs}), 70)
        self.assertEqual(Counter(ref["language"] for ref in refs),
                         {"python": 26, "typescript": 27, "javascript": 3, "go": 3,
                          "rust": 6, "bash": 2, "lua": 2, "lisp": 1})
        scanned = {}
        excluded = {"exercises", "tests", "compat", "__pycache__", "target", "build",
                    "dist", "node_modules", "generated", ".pytest_cache", ".venv", "venv"}
        self.assertEqual(set(IMPLEMENTATION_ROOTS), set(SUFFIXES))
        for language, suffix in SUFFIXES.items():
            root = REPO / IMPLEMENTATION_ROOTS[language]
            self.assertTrue(root.is_dir(), root)
            for path in root.rglob("*" + suffix):
                if (not path.is_file() or excluded.intersection(path.relative_to(root).parts)
                        or path.name == "__init__.py" or path.name.startswith("test_")
                         or path.name.endswith((".spec.ts", ".spec.js", ".test.ts", ".test.js",
                                                "_test.go", "_test.py"))):
                    continue
                scanned[str(path.relative_to(REPO))] = (language, source_topic(path))
        declared = {ref["path"]: (ref["language"], topic)
                    for topic, row in rows.items() for ref in row["references"]}
        self.assertEqual(set(declared), set(scanned))
        for path in scanned:
            with self.subTest(reference=path):
                self.assertEqual(declared[path], scanned[path])
        self.assertTrue(all((REPO / ref["path"]).is_file() for ref in refs))
        bindings = [binding for row in rows.values() for binding in row["bindings"]]
        self.assertCountEqual(bindings, IDS)
        self.assertEqual({key for key, row in rows.items() if row["bindings"]}, set(QUESTIONS))
        self.assertEqual(rows["spiral-matrix"]["references"], [])
        self.assertEqual({ref["language"] for ref in rows["hello-world"]["references"]},
                         {"python", "rust", "javascript", "go", "bash", "lua", "lisp"})
        for topic in ("stack", "queue"):
            self.assertEqual([ref["language"] for ref in rows[topic]["references"]], ["python"])
        self.assertEqual({ref["language"] for ref in rows["boggle"]["references"]}, {"python", "typescript"})
        self.assertEqual([ref["language"] for ref in rows["two-sum"]["references"]], ["typescript"])
        pivot = {ref["language"]: ref for ref in rows["find-pivot-index"]["references"]}
        self.assertFalse((REPO / pivot["python"]["path"]).read_text().strip())
        self.assertIn("placeholder", (pivot["python"]["note"] or "").lower())
        self.assertTrue((REPO / pivot["typescript"]["path"]).read_text().strip())

    def test_metadata_human_rows_and_json_need_no_git_tools_or_root_files(self):
        rows = self.inventory()
        shutil.rmtree(self.root)
        self.root.mkdir()
        env = {**self.env, "PATH": ""}
        before = self.sources()
        self.assertEqual(self.inventory(env), rows)
        self.assertEqual(self.inventory(env, arguments=()), rows)
        output = self.cli("questions", "--pretty", env=env)
        self.assertNotIn("\t", output)
        self.assertNotIn("\x1b", output)
        self.assertTrue(output.isascii())
        self.assertTrue(all(len(line) < 80 for line in output.splitlines()))
        header = output.splitlines()[0]
        self.assertIn("Problem ID", header)
        question_column = header.index("Question")
        references_column = header.index("Solutions")
        self.assertEqual(references_column, 47)
        practice_column = header.index("Practice")
        table = {}
        current = None
        for line in output.splitlines()[2:]:
            if line.startswith("---"):
                break
            topic = line[:question_column].strip()
            if topic:
                self.assertIn(topic, rows)
                self.assertNotIn(topic, table)
                current = table[topic] = {
                    "question": line[question_column:references_column].strip(),
                    "references": [], "practice": [],
                }
            self.assertIsNotNone(current)
            for name, value in (
                ("references", line[references_column:practice_column].strip()),
                ("practice", line[practice_column:].strip()),
            ):
                if value:
                    current[name].append(value)
        self.assertEqual(set(table), set(rows))
        for topic, row in rows.items():
            displayed = table[topic]
            self.assertEqual(displayed["question"], row["question_status"])
            languages = " ".join(displayed["references"])
            self.assertCountEqual([] if languages == "-" else languages.split(", "),
                                   {ref["language"] for ref in row["references"]})
            practice = " ".join(displayed["practice"])
            self.assertCountEqual([] if practice == "-" else practice.split(", "),
                                  {binding.split("/", 1)[0] for binding in row["bindings"]})
        self.assertIn("'-' means not converted", output)
        self.assertRegex(output, r"Solutions: .*not all checked.*'-' means none")
        self.assertIn("polyglot question <problem-id>", output)
        for pattern in (r"37\s+topics", r"20\s+(?:question\s+)?docs", r"70\s+solution artifacts",
                        r"10\s+(?:native\s+)?bindings"):
            self.assertRegex(output, pattern)
        self.assertEqual([line.split("\t")[0] for line in self.cli("list", env=env).splitlines()], list(IDS))
        for args in (("questions", "--json", "extra"), ("questions", "--json", "--json"),
                     ("questions", "--pretty", "--pretty"), ("questions", "--json", "--pretty"),
                     ("questions", "--pretty", "--json"), ("questions", "--pretty", "extra"),
                     ("questions", "--language", "python"), ("question", "--json"),
                     ("question", "boggle", "extra"), ("list", "--language", "typescript")):
            self.assert_blocked(*args, env=env)
        self.assertEqual(self.sources(), before)
        self.assertFalse((self.root / ".git").exists())

    def test_all_details_are_read_only_without_references_git_or_tools(self):
        rows = self.inventory()
        shutil.rmtree(self.root / ".git")
        shutil.rmtree(self.root / "practice")
        # Poison a declared reference: detail must display metadata, never read or run it.
        reference = self.root / "practice/python/soutions/boggle.py"
        reference.parent.mkdir(parents=True)
        reference.symlink_to(self.base / "nonexistent implementation")
        env = {**self.env, "PATH": ""}
        before = self.sources()
        for topic, row in rows.items():
            with self.subTest(topic=topic):
                output = self.cli("question", topic, env=env)
                self.assertIn(row["title"], output)
                self.assertIn(row["question_status"], output.lower())
                self.assertRegex(output, r"Solutions \(.*not all checked.*not runnable exercise bindings\)")
                for ref in row["references"]:
                    self.assertIn(ref["path"], output)
                for binding in row["bindings"]:
                    self.assertIn(binding, output)
                if row["question_doc"]:
                    body = (self.root / row["question_doc"]).read_text().strip()
                    if body:
                        self.assertIn(body, output)
                    else:
                        self.assertRegex(output.lower(), r"placeholder|empty")
                    if row["question_status"] == "draft":
                        self.assertRegex(output.lower(), r"unvalidated|not validated")
                else:
                    self.assertRegex(output.lower(), r"missing|no question")
                    self.assertNotIn("Prompt:", output)
        self.assertEqual(self.sources(), before)
        self.assertFalse((self.root / ".git").exists())

    def test_draft_doc_validation_and_static_status_do_not_promote_practice(self):
        path = self.root / "README/katas/boggle.md"
        original = path.read_bytes()
        path.write_text("# Fully rewritten question\nRuntime draft marker 72913.\n")
        self.assertIn("Runtime draft marker", self.cli("question", "boggle"))
        self.assertEqual(self.inventory()["boggle"]["question_status"], "draft")
        outside = self.base / "outside document"
        outside.write_bytes(original)
        for kind in ("missing", "invalid utf8", "symlink", "directory", "unreadable"):
            with self.subTest(kind=kind):
                path.unlink()
                if kind == "invalid utf8":
                    path.write_bytes(b"\xff\xfe")
                elif kind == "symlink":
                    path.symlink_to(outside)
                elif kind == "directory":
                    path.mkdir()
                elif kind == "unreadable":
                    path.write_bytes(original)
                    path.chmod(0)
                try:
                    if kind != "unreadable" or not os.access(path, os.R_OK):
                        # Snapshot helpers intentionally read files, so snapshot around chmod separately.
                        metadata = self.git_files()
                        output = (self.cli("question", "boggle", code=2) if kind == "unreadable"
                                  else self.assert_blocked("question", "boggle"))
                        self.assertIn("Blocked:", output)
                        self.assertIn(str(path), output)
                        self.assertEqual(self.git_files(), metadata)
                finally:
                    if path.is_dir() and not path.is_symlink():
                        path.rmdir()
                    elif path.exists() or path.is_symlink():
                        path.unlink()
                    path.write_bytes(original)
                self.assertEqual(outside.read_bytes(), original)
        directory = path.parent
        moved = self.base / "outside draft docs"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
        try:
            self.assert_blocked("question", "boggle")
        finally:
            directory.unlink()
            moved.rename(directory)
        path = self.root / "README/katas/hello_world.md"
        path.write_bytes(b"\xff")
        self.assert_blocked("question", "hello-world")

    def test_inventory_only_topics_and_guessed_bindings_never_become_runnable(self):
        env = {**self.env, "PATH": ""}
        for topic in sorted(DRAFTS | MISSING):
            for selection in (topic, "python/" + topic.replace("-", "_"),
                              "rust/" + topic.replace("-", "_")):
                for command in ("show", "start", "practice", "check", "reset", "hint"):
                    with self.subTest(command=command, selection=selection):
                        self.assert_blocked(command, selection, env=env)
        self.assertEqual([line.split("\t")[0] for line in self.cli("list").splitlines()], list(IDS))


if __name__ == "__main__":
    unittest.main()
