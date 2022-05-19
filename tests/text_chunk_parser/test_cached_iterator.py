# -*- coding: utf-8 -*-
#
#  test_cached_iterator.py
#  _project_
#
#  Created by Chad Lowe on 2022-05-19.
#  Copyright 2022 Chad Lowe. All rights reserved.
#
from pfmsoft.text_chunk_parser.cached_iterator import CachedIterator


def test_cached_iterator():
    data = list(range(7))
    cached_iter = CachedIterator(iter(data))
    value = next(cached_iter)
    assert value == 0
    assert len(cached_iter.past) == 1
    assert cached_iter.past[0] == value
    assert len(cached_iter.peek) == 3
    assert cached_iter.peek[-1] == 3
    value = next(cached_iter)
    assert value == 1
    value = next(cached_iter)
    assert value == 2
    value = next(cached_iter)
    assert value == 3
    value = next(cached_iter)
    assert value == 4
    value = next(cached_iter)
    assert value == 5
    assert len(cached_iter.past) == 3
    assert len(cached_iter.peek) == 1
    assert cached_iter.past[0] == value
    assert cached_iter.past[1] == value - 1
    assert cached_iter.peek[-1] == 6
    value = next(cached_iter)
    assert value == 6


def test_iter_less_than_peek():
    cached_iter = CachedIterator(iter(range(2)), past_size=3, peek_size=3)
    assert len(cached_iter.peek) == 3
    assert len(cached_iter.past) == 0
    print("past", cached_iter.past)
    print("peek", cached_iter.peek)
    value = next(cached_iter)
    assert len(cached_iter.peek) == 1
    assert len(cached_iter.past) == 1
    print("past", cached_iter.past)
    print("peek", cached_iter.peek)
    assert value == 0
    value = next(cached_iter)
    assert len(cached_iter.peek) == 0
    assert len(cached_iter.past) == 2
    print("past", cached_iter.past)
    print("peek", cached_iter.peek)
    assert value == 1
