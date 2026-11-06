import unittest

from exercises.find_in_string import find_in_string
from tests.feedback import assert_expected


class PracticeTests(unittest.TestCase):
    longMessage = False

    def test_find_in_string(self):
        cases = [
            ("Dawson, Jamal", "Jamal", 8),
            ("banana", "ana", 1),
            ("abc", "a", 0),
            ("abc", "c", 2),
            ("abc", "abc", 0),
            ("abc", "z", -1),
            ("a", "abc", -1),
            ("abc", "A", -1),
            ("abc", "", 0),
            ("", "", 0),
            ("", "a", -1),
            ("x" * 300 + "end", "end", 300),
        ]
        for string, substring, expected in cases:
            with self.subTest(string=string, substring=substring):
                result = find_in_string(string, substring)
                self.assertIs(
                    type(result), int,
                    msg=f"Your result: {result!r} (type: {type(result).__name__})\nExpected result type: int",
                )
                assert_expected(self, result, expected, label="result")
