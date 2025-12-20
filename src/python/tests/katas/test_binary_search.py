import pytest
from katas.binary_search import binary_search


@pytest.mark.xfail(
    reason="binary_search assumes ascending-sorted input; unsorted behavior is undefined"
)
def test_binary_search_unsorted_array():
    arr = [3, 1, 2]
    assert binary_search(1, arr) is False


@pytest.mark.parametrize(
    "arr,target,expected",
    [
        # happy path (sorted input, hits & misses)
        ([1, 3, 5, 7, 9], 1, True),  # first
        ([1, 3, 5, 7, 9], 5, True),  # middle
        ([1, 3, 5, 7, 9], 9, True),  # last
        ([1, 3, 5, 7, 9], 6, False),  # between values
        ([], 42, False),  # empty
        ([4], 4, True),  # singleton hit
        ([4], 5, False),  # singleton miss
        ([2, 2, 2, 2], 2, True),  # duplicates
    ],
)
def test_binary_search(arr, target, expected):
    assert binary_search(target, arr) is expected
