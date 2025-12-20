def fibonacci(length):
    if length <= 0:
        return []
    if length == 1:
        return [1]
    prev_1 = 1
    prev_2 = 1
    sequence = [prev_1, prev_2]
    for i in range(length-2):
        new_number = prev_1 + prev_2
        sequence.append((new_number))
        if i % 2 == 0:
            prev_1 = new_number
        else:
            prev_2 = new_number
    return sequence


length = 22
print(f"Your fibonacci sequence of length {length}")
print(fibonacci(length))
