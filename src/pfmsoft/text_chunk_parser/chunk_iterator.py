# -*- coding: utf-8 -*-
#
#  chunk_iterator.py
#  _project_
#
#  Created by Chad Lowe on 2022-05-19.
#  Copyright 2022 Chad Lowe. All rights reserved.
#

import re
from logging import NullHandler, getLogger
from typing import Any, Callable, Iterable, Tuple

from pfmsoft.text_chunk_parser.cached_iterator import CachedIterator
from pfmsoft.text_chunk_parser.enumerated_filtered_iterator import (
    Enumerated,
    EnumeratedFilteredIter,
)

logger = getLogger(__name__)
logger.addHandler(NullHandler())


def blank_lines(count: int, text: str) -> bool:
    """
    An example of a filter function that can be used with ChunkIterator.
    This function will skip blank lines.
    """
    regex = r"^(?P<whitespace>[^\S\n]*)\n$"
    empty_line_pattern = re.compile(regex)
    match = empty_line_pattern.match(text)
    if match:
        logger.info(
            "Line number %s has only white space.",
            count,
        )
        return False
    return True


class Chunk:
    def __init__(
        self,
        value: Enumerated,
        peek: Tuple[Enumerated, ...] = (),
        past: Tuple[Enumerated, ...] = (),
        source: str = "",
    ):
        self.value = value
        self.peek = peek
        self.past = past
        self.source = source

    @property
    def text(self):
        return self.value.value

    @property
    def count(self):
        return self.value.count

    def __repr__(self):
        return (
            f"{__class__.__name__}("
            f"value={self.value}, "
            f"peek={self.peek}, "
            f"past={self.past}, "
            f"source={self.source!r}, "
            f")"
        )

    def __str__(self):
        return (
            f"{__class__.__name__}("
            f"{self.value.count}: `{self.value.value}`"
            f", source={self.source!r}"
            f")"
        )


class ChunkIterator:
    def __init__(
        self,
        iterable: Iterable,
        source: str = "",
        chunk_filter: Callable[[int, Any], bool] | None = blank_lines,
        past_size: int = 3,
        peek_size: int = 3,
    ):
        """
        Args:
            iterable: Iterable source of text to be chunked.
            source: The name of the source. Defaults to "".
            chunk_filter: A filter function that can be used to skip chunks of text.
                Defaults to blank_lines.
            history_size: The size of the history buffer. Defaults to 3.
            peek_size: The size of the peek buffer. Minimum 1. Defaults to 3.
        """

        self.source = source
        self.past_size = max(past_size, 1)
        self.peek_size = max(peek_size, 1)
        self.chunk_filter = chunk_filter
        enum_filtered = EnumeratedFilteredIter(iterable, self.chunk_filter)
        cached = CachedIterator(
            enum_filtered, past_size=self.past_size, peek_size=self.peek_size
        )
        self.iterable = cached

    def __iter__(self):
        return self

    def __next__(self) -> Chunk:
        value: Enumerated = next(self.iterable)
        past = tuple(self.iterable.past)
        peek = tuple(self.iterable.peek)
        return Chunk(value=value, past=past, peek=peek, source=self.source)
