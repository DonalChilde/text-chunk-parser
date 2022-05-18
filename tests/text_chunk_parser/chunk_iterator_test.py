from io import StringIO
from pprint import PrettyPrinter
from typing import List

from pfmsoft.text_chunk_parser import ChunkIterator
from pfmsoft.text_chunk_parser.text_chunk_parser import Chunk

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
PP = PrettyPrinter(indent=4)


def test_init_cache():
    provider = ChunkIterator(StringIO(JSON_DICT), "Json Dict")
    assert len(provider.peek) == 0
    chunk = next(provider)
    assert len(provider.peek) == 3
    assert provider.peek[0].ident == "5"
    assert chunk.morsel().ident == "2"


def test_advance_iterator():
    provider = ChunkIterator(StringIO(JSON_DICT), "Json Dict")
    chunks: List[Chunk] = []
    for chunk in provider:
        chunks.append(chunk)
        print(chunk)
    assert len(chunks) == 11
    print(repr(chunks[5]))
    print(chunks[5].morsel())
    # assert False
