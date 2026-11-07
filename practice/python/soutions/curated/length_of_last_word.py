def length_of_last_word(text: str) -> int:
    words = text.split()
    return len(words[-1]) if words else 0
