from katas.remove_element import remove_element

def test_remove_element():
    nums = [3,2,2,3]
    val = 3
    result = remove_element(nums, val)
    expected = 2
    assert result is expected
