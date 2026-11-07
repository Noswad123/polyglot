"""Persistent layout checks; legacy servers and databases are never executed."""

import json
import stat
import unittest

from active_fixture import REPO
from test_library_inventory import IMPLEMENTATION_ROOTS


class SolutionsLayoutTests(unittest.TestCase):
    def test_language_directories(self):
        for language, relative in IMPLEMENTATION_ROOTS.items():
            with self.subTest(language=language):
                self.assertTrue((REPO / relative).is_dir())

    def test_supporting_tests_and_manifests(self):
        self.assertEqual(len(list((REPO / IMPLEMENTATION_ROOTS["typescript"]).glob("*.spec.ts"))), 17)
        package = json.loads((REPO / "practice/typescript/package.json").read_text())
        self.assertIs(package["private"], True)
        self.assertEqual(package["devDependencies"], {"typescript": "5.9.3"})
        lock = json.loads((REPO / "practice/typescript/package-lock.json").read_text())
        self.assertEqual(lock["packages"]["node_modules/typescript"]["version"], "5.9.3")
        for language, relative in (
            ("javascript", "package.json"),
            ("go", "users/go.mod"),
            ("go", "users/go.sum"),
            ("rust", "users/Cargo.toml"),
            ("rust", "users/Cargo.lock"),
        ):
            with self.subTest(language=language, path=relative):
                self.assertTrue((REPO / IMPLEMENTATION_ROOTS[language] / relative).is_file())

    def test_users_databases_have_sqlite_headers(self):
        for language in ("go", "rust"):
            with self.subTest(language=language):
                with (REPO / IMPLEMENTATION_ROOTS[language] / "users/users.db").open("rb") as database:
                    self.assertEqual(database.read(16), b"SQLite format 3\x00")

    def test_executable_modes_retained(self):
        for language, relative in (("bash", "hello_world.sh"), ("bash", "pong.sh"),
                                   ("go", "helloWorld.go")):
            with self.subTest(language=language, path=relative):
                mode = (REPO / IMPLEMENTATION_ROOTS[language] / relative).stat().st_mode
                self.assertEqual(stat.S_IMODE(mode), 0o755)


if __name__ == "__main__":
    unittest.main()
