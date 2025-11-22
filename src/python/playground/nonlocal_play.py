def outer():
    x = 10

    def inner():
        nonlocal x  # refers to 'x' in outer()
        x += 5
        print("Inner:", x)

    inner()
    print("Outer:", x)

outer()
