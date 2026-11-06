import unittest

from exercises.fibonacci import fibonacci
from tests.feedback import assert_expected


# Fixed contract fixture, independent of the learner's implementation.
TERMS = [
    1, 1, 2, 3, 5, 8, 13, 21, 34, 55,
    89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765,
    10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811,
    514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465,
    14930352, 24157817, 39088169, 63245986, 102334155,
]


class PracticeTests(unittest.TestCase):
    longMessage = False

    def test_fibonacci(self):
        for length in range(41):
            with self.subTest(length=length):
                result = fibonacci(length)
                self.assertIs(
                    type(result), list,
                    msg=f"Your result: {result!r} (type: {type(result).__name__})\nExpected result type: list",
                )
                for term in result:
                    self.assertIs(
                        type(term), int,
                        msg=f"Your result term: {term!r} (type: {type(term).__name__})\nExpected result term type: int",
                    )
                assert_expected(self, result, TERMS[:length], label="result")
