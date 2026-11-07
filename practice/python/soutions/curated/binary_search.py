def binary_search(target: int, arr: list[int]) -> bool:
    low, high = 0, len(arr)
    while low < high:
        middle = low + (high - low) // 2
        if arr[middle] == target:
            return True
        if arr[middle] < target:
            low = middle + 1
        else:
            high = middle
    return False
