import io
import unittest
from contextlib import redirect_stdout

from exercises.hello import hello
from tests.feedback import assert_expected


class PracticeTests(unittest.TestCase):
    longMessage = False

    def test_hello(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = hello()
        assert_expected(self, output.getvalue(), "Hello, World!\n", label="output")
        self.assertIsNone(
            result,
            msg=f"Your return value: {result!r}\nExpected return value: None",
        )
