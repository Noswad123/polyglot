from katas.rotate_array import rotate


def test_rotate_array2():
    nums = [-1, -100, 3, 99]
    k = 2
    expected = [3, 99, -1, -100]
    rotate(nums, k)
    assert nums == expected

def test_rotate_array_two():
    nums = [1, 2, 3, 4, 5, 6, 7]
    k = 3
    expected = [4, 5, 6, 7, 1, 2, 3]
    rotate(nums, k)
    assert nums == expected
