# -*- coding: utf-8 -*-
#
#  filtered_iterator.py
#  _project_
#
#  Created by Chad Lowe on 2022-05-19.
#  Copyright 2022 Chad Lowe. All rights reserved.
#

from typing import Callable, Iterable


class FilteredIterable:
    def __init__(
        self,
        iterable: Iterable,
        filter_: Callable[..., bool] | None = None,
    ):
        self.iterable = iterable
        self.filter = filter_
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        success = False
        while not success:
            value = next(self.iterable)
            success = self.filter(value)
        return value
