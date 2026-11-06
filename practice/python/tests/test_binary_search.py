import unittest

from exercises.binary_search import binary_search
from tests.feedback import assert_expected


class PracticeTests(unittest.TestCase):
    longMessage = False

    def test_binary_search(self):
        # These behavior checks do not prove the algorithm's complexity.
        cases = [
            (1, [], False),
            (5, [5], True),
            (4, [5], False),
            (6, [5], False),
            (-8, [-8, -3, 0, 4, 9, 12], True),
            (12, [-8, -3, 0, 4, 9, 12], True),
            (0, [-8, -3, 0, 4, 9, 12], True),
            (-9, [-8, -3, 0, 4, 9, 12], False),
            (13, [-8, -3, 0, 4, 9, 12], False),
            (5, [-8, -3, 0, 4, 9, 12], False),
            (2, [1, 2, 2, 2, 3], True),
            (4, [1, 2, 2, 2, 3], False),
            (7, [7, 7, 7, 7], True),
            (6, [7, 7, 7, 7], False),
            (1, [1, 2], True),
            (2, [1, 2], True),
        ]
        for target, arr, expected in cases:
            with self.subTest(target=target, arr=arr):
                original = arr.copy()
                result = binary_search(target, arr)
                self.assertIs(
                    type(result), bool,
                    msg=f"Your result: {result!r} (type: {type(result).__name__})\nExpected result type: bool",
                )
                assert_expected(self, result, expected, label="result")
                assert_expected(self, arr, original, label="input after call")
