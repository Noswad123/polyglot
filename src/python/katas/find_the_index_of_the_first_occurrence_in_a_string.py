def find_in_string(string: str, sub_string: str) -> int:
    if sub_string == "":
        return 0
    for i in range(len(string) + 1 - len(sub_string)):
        if string[i: i + len(sub_string)] == sub_string:
            return i
    return -1

