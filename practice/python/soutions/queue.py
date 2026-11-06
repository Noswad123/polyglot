from collections import deque


class Queue:
    """A simple first-in, first-out (FIFO) queue."""

    def __init__(self):
        self._items = deque()

    def enqueue(self, item):
        """Add an item to the back of the queue."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return the item at the front of the queue."""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def peek(self):
        """Return the front item without removing it."""
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._items[0]

    def is_empty(self):
        """Return True if the queue has no items."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the queue."""
        return len(self._items)


if __name__ == "__main__":
    queue = Queue()
    queue.enqueue("first")
    queue.enqueue("second")
    queue.enqueue("third")

    print("Front item:", queue.peek())
    print("Queue size:", queue.size())

    while not queue.is_empty():
        print("Dequeued:", queue.dequeue())
