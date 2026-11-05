"""Check local answers with Python's standard-library unittest runner."""

import io
import unittest
from contextlib import redirect_stdout

from answers import find_in_string, hello, length_of_last_word


class PracticeTests(unittest.TestCase):
    def test_hello(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = hello()
        self.assertEqual(output.getvalue(), "Hello, World!\n")
        self.assertIsNone(result)

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
                self.assertIs(type(result), int)
                self.assertEqual(result, expected)

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
                self.assertIs(type(result), int)
                self.assertEqual(result, expected)
