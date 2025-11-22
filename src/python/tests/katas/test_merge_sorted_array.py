from katas.merge_sorted_array import merge_sorted_array

def test_mergeSortedArray():
    nums1 = [0]
    m = 0
    nums2 = [1]
    n = 1
    result = merge_sorted_array(nums1, m, nums2, n)
    expected = [1]
    assert result == expected

def test_mergeSortedArray_two():
    nums1 = [4,5,6,0,0,0]
    m = 3
    nums2 = [1,2,3]
    n = 3
    result = merge_sorted_array(nums1, m, nums2, n)
    expected = [1,2,3,4,5,6]
    assert result == expected
