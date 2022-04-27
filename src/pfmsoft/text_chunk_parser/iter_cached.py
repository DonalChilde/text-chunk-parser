from collections import deque
from itertools import chain
from typing import Any, Deque, Iterable


class IterCached:
    def __init__(
        self,
        iterable: Iterable,
        history_size: int = 3,
        peek_size: int = 3,
        placeholder: Any = ...,
    ) -> None:
        self.iterable = chain(iterable, (placeholder for _ in range(peek_size)))
        self.history_size = history_size
        self.peek_size = peek_size
        self.placeholder = placeholder
        self.peek_deque: Deque = deque(maxlen=peek_size)
        self.history_deque: Deque = deque(maxlen=history_size + 1)

    def _advance_deque(self):
        for _ in range(self.peek_size):
            self._advance_deque()
            while True:
                value = self.peek_deque.pop()
                self.history_deque.append(value)
                try:
                    new_value = next(self.iterable)
                    self.peek_deque.append(new_value)
                except StopIteration as exc:
                    _ = exc
                    return
                yield value

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._advance_deque)

    def peek(self):
        pass

    def history(self):
        pass

    # FIXME add get from index, __str__ output, __repr__,
