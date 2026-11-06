def assert_expected(test, actual, expected, *, label):
    message = f"Your {label}: {actual!r}\nExpected {label}: {expected!r}"
    if isinstance(actual, str) or isinstance(expected, str):
        message += "\n" + r"Whitespace: \n = newline; \t = tab."
    test.assertEqual(actual, expected, msg=message)
