from io import StringIO

import pytest

from pfmsoft.text_chunk_parser.iter_cached import IterCached

JSON_DICT = """
foo = {
    "Name": "B. S. Johnson",
    "Profession": "Engineer",
    "Location": "Unknown",
    "Notable Creations": [
        "Archchancellor's Bathroom",
        "Colossus of Ankh-Morpork",
        "Hanging Gardens of Ankh",
        "Quirm Memorial",
    ],
}
"""


def test_peek():
    raise NotImplementedError


def test_history():
    raise NotImplementedError


def test_current_value():
    iter_cache = IterCached(StringIO(JSON_DICT))
    for count, value in enumerate(iter_cache):
        print(count, value)
        assert value == iter_cache.current()


def test_consume_all():
    iter_cache = IterCached(StringIO(JSON_DICT))
    string_iter = StringIO(JSON_DICT)
    assert tuple(iter_cache) == tuple(string_iter)
    print(iter_cache)
