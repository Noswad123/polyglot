
from typing import List

def running_total(nums: List[int]) -> int:
    total = 0
    for num in nums:
        total += num
    return total

nums = [1,2,3,4,5]
print(running_total(nums))
