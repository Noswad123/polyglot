import pytest
from katas.find_in_string import find_in_string


@pytest.mark.parametrize(
    "string, substring, expected",
    [
        ["Dawson, Jamal", "Jamal", 8]
    ],
)
def test_find_in_string(string, substring, expected):
    assert find_in_string(string, substring) is expected
