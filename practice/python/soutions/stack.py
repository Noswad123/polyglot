class Stack:
    """A simple last-in, first-out (LIFO) stack."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item from the stack."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        """Return True if the stack has no items."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self._items)


if __name__ == "__main__":
    stack = Stack()
    stack.push("first")
    stack.push("second")
    stack.push("third")

    print("Top item:", stack.peek())
    print("Stack size:", stack.size())

    while not stack.is_empty():
        print("Popped:", stack.pop())
