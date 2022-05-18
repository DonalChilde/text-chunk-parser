from collections import deque
from itertools import chain, islice
from typing import Any, Deque, Iterable


class IterCached:
    def __init__(
        self,
        iterable: Iterable,
        history_size: int = 3,
        peek_size: int = 3,
        placeholder: Any = ...,
    ) -> None:
        cache_size = history_size + peek_size + 1
        self.iterable = chain(iterable, (placeholder for _ in range(peek_size)))
        self.history_size = history_size
        self.peek_size = peek_size
        self.placeholder = placeholder
        self.cached: Deque = deque(maxlen=cache_size)
        self._initialize_cache()

    def _initialize_cache(self):
        if self.peek_size > 0:
            for _ in range(self.peek_size):
                value = next(self.iterable)
                self.cached.appendleft(value)

    def _advance_cache(self) -> Any:
        """
        Get the next value from peek, or iterator
        """
        iter_value = next(self.iterable)
        self.cached.appendleft(iter_value)
        current_value_index = self.peek_size
        return self.cached[current_value_index]

    def __str__(self):
        start_index = self.peek_size
        cached_string = []
        current_index = start_index
        for item in self.cached:
            cached_string.append(f"[{current_index}] {item!r}")
            current_index -= 1
        return "\n".join(cached_string)

    def __iter__(self):
        return self

    def __next__(self):

        return self._advance_cache()

    def current(self):
        return self.cached[self.peek_size]

    def peek(self):
        return tuple(reversed(tuple(islice(self.cached, 0, self.peek_size))))

    def history(self):
        return tuple(islice(self.cached, self.peek_size + 1, len(self.cached)))

    # FIXME add get from index, __str__ output, __repr__,
