import pytest
from katas.fibonacci import fibonacci


@pytest.mark.parametrize(
    "length,expected",
    [
        (0, []),
        (1, [1]),
        (4, [1, 1, 2, 3]),
        (8, [1, 1, 2, 3, 5, 8, 13, 21]),
        (
            22,
            [
                1,
                1,
                2,
                3,
                5,
                8,
                13,
                21,
                34,
                55,
                89,
                144,
                233,
                377,
                610,
                987,
                1597,
                2584,
                4181,
                6765,
                10946,
                17711,
            ],
        ),
    ],
)
def test_fibonacci(length, expected):
    assert fibonacci(length) == expected
