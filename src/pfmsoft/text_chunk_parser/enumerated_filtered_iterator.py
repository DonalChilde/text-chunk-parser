# -*- coding: utf-8 -*-
#
#  enumerated_filtered_iterator.py
#  _project_
#
#  Created by Chad Lowe on 2022-05-19.
#  Copyright 2022 Chad Lowe. All rights reserved.
#


from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass
class Enumerated:
    count: int
    value: Any


class EnumeratedFilteredIter:
    def __init__(
        self,
        iterable: Iterable,
        filter_: Callable[[int, Any], bool] | None = None,
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
            self.count += 1
            success = self.filter(self.count, value)
        return Enumerated(self.count, value)
