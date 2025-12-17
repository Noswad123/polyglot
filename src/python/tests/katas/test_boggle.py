import pytest
from katas.boggle import is_word_present

@pytest.fixture
def board1():
    return [
        ['h', 'p', 'g', 'e'],
        ['o', 'o', 'a', 'r'],
        ['i', 't', 'p', 'u'],
        ['s', 'y', 'h', 'n']
    ]

@pytest.mark.parametrize("word,expected", [
    ("pure", True),
    ("hog", True),
    ("hoist", True),
    ("hoists", False),
    ("reap", True),
    ("harp", False),
])
def test_board1_words(board1, word, expected):
    assert is_word_present(board1, word) == expected
