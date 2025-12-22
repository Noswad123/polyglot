def find_in_string(string: str, substring: str) -> int:
    if substring == "":
        return 0

    string_length = len(string)
    substring_length = len(substring)

    if string_length < substring_length:
        return -1

    for i in range(string_length + 1 - substring_length):
        if string[i: i + substring_length] == substring:
            return i
    return -1


print(find_in_string("Dawson, Jamal", "Jamal"))
