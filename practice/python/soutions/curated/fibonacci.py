def fibonacci(length: int) -> list[int]:
    terms: list[int] = []
    first, second = 1, 1
    for _ in range(length):
        terms.append(first)
        first, second = second, first + second
    return terms
