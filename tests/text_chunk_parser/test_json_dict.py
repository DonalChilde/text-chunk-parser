import pytest
from tests.text_chunk_parser.examples.json_dict import (
    JSON_DICT,
    EmptyLine,
    IdentifierLine,
    KeyValueLine,
)

from pfmsoft.text_chunk_parser import ParseContext, Parser, StringChunkProvider
from pfmsoft.text_chunk_parser.text_chunk_parser import Chunk, FailedParseException


def test_identier_parse():
    with StringChunkProvider(JSON_DICT) as provider:
        chunk = next(provider)
        chunk = next(provider)
        state, data = IdentifierLine().parse(chunk, "origin", None)
    assert state == "identifier"
    assert data == {"identifier": "foo", "terminus": "{"}


def test_identifier_parse_fail():
    with StringChunkProvider(JSON_DICT) as provider:
        chunk = next(provider)
        with pytest.raises(FailedParseException) as exc:
            _, _ = IdentifierLine().parse(chunk, "origin", None)
            assert exc.state == "origin"
            assert exc.parser is FailedParseException
            assert exc.chunk == chunk


def test_empty_line_parse():
    with StringChunkProvider(JSON_DICT) as provider:
        chunk = next(provider)
        state, data = EmptyLine().parse(chunk, "origin", None)
    assert state == "empty_line"
    assert data == {"whitespace": ""}

    chunk = Chunk("1", "   \n")
    state, data = EmptyLine().parse(chunk, "origin", None)
    assert state == "empty_line"
    assert data == {"whitespace": "   "}


def test_empty_line_parse_fail():
    with StringChunkProvider(JSON_DICT) as provider:
        chunk = next(provider)
        chunk = next(provider)
        with pytest.raises(FailedParseException) as exc:
            _, _ = EmptyLine().parse(chunk, "origin", None)
            assert exc.state == "origin"
            assert exc.parser is FailedParseException
            assert exc.chunk == chunk


def test_key_value_line():
    with StringChunkProvider(JSON_DICT) as provider:
        chunk = next(provider)
        chunk = next(provider)
        chunk = next(provider)
        state, data = KeyValueLine().parse(chunk, "origin", None)
    assert state == "key_value"
    assert data == {"key": "Name", "value": "B. S. Johnson"}
