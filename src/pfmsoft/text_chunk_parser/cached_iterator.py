# -*- coding: utf-8 -*-
#
#  cached_iterator.py
#  _project_
#
#  Created by Chad Lowe on 2022-05-19.
#  Copyright 2022 Chad Lowe. All rights reserved.
#

from collections import deque
from typing import Deque, Iterator


class PlaceHolder:
    def __repr__(self):
        return f"{__class__.__name__}()"


class CachedIterator:
    def __init__(
        self,
        iterable: Iterator,
        past_size: int = 3,
        peek_size: int = 3,
    ) -> None:
        self.iterable = iterable
        self.past_size = max(past_size, 1)
        self.peek_size = max(peek_size, 1)
        self.peek: Deque = deque(maxlen=self.peek_size)
        self.past: Deque = deque(maxlen=self.past_size)
        self.place_holder = PlaceHolder()
        for _ in range(self.peek_size):
            self.peek.append(self.place_holder)
        self.peek_primed: bool = False
        self.iter_exhausted: bool = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self.peek_primed:
            self._init_peek()
        iter_value = self._advance_iter()
        try:
            return_value = self.peek.popleft()
            self.past.appendleft(return_value)
            # Dont try to add more items after iter exhausted
            if not self.iter_exhausted:
                self.peek.append(iter_value)
            return return_value
        except IndexError as exc:
            raise StopIteration from exc

    def _advance_iter(self):
        try:
            iter_value = next(self.iterable)
            return iter_value
        except StopIteration:
            self.iter_exhausted = True
            return self.place_holder

    def _init_peek(self):
        try:
            while not self.peek_primed:
                self.peek.append(next(self.iterable))
                if self.peek[0] != self.place_holder:
                    self.peek_primed = True
        except StopIteration as exc:
            # self.iterator had no values
            if self.peek[-1] == self.place_holder:
                raise exc
            # advance self.peek til leftmost value is from iterator
            while self.peek and self.peek[0] == self.place_holder:
                self.peek.popleft()
            # Somehow peek had no values. this should not happen.
            if not self.peek:
                raise exc
