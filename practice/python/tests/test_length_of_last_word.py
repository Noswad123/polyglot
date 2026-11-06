import unittest

from exercises.length_of_last_word import length_of_last_word
from tests.feedback import assert_expected


class PracticeTests(unittest.TestCase):
    longMessage = False

    def test_length_of_last_word(self):
        cases = [
            ("Hello World", 5),
            ("   fly me   to   the moon  ", 4),
            ("single", 6),
            ("", 0),
            ("   ", 0),
            (" \t\n", 0),
            ("hello\tworld", 5),
            ("hello\nworld\n", 5),
            ("hello world!", 6),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                result = length_of_last_word(text)
                self.assertIs(
                    type(result), int,
                    msg=f"Your result: {result!r} (type: {type(result).__name__})\nExpected result type: int",
                )
                assert_expected(self, result, expected, label="result")
