def func1():
    raise ValueError("bad value")


def func2():
    raise TypeError("bad type")


def func3():
    return "ok"


errors = []
for f in [func1, func2, func3]:
    try:
        f()
    except Exception as e:
        errors.append(e)

if errors:
    raise ExceptionGroup("Multiple errors occurred", errors)
