import logging
from dataclasses import dataclass, field
from pickle import FALSE
from typing import Dict, Sequence

import pytest
from tests.text_chunk_parser.examples.json_dict import (
    JSON_DICT,
    DictEndLine,
    IdentifierLine,
    JsonParseContext,
    JsonParseSchema,
    KeyListLine,
    KeyValueLine,
    ListEndLine,
    ListValueLine,
)

from pfmsoft.text_chunk_parser import (
    Chunk,
    EmptyLine,
    FailedParseException,
    Parser,
    StringChunkProvider,
)
from pfmsoft.text_chunk_parser.text_chunk_parser import (
    AllFailedToParseException,
    ChunkParser,
)


@dataclass
class ParseTest:
    text: str
    state: str
    data: Dict = field(default_factory=dict)


def test_parse_schema(caplog):
    caplog.set_level(logging.INFO)
    context = JsonParseContext()
    schema = JsonParseSchema()
    parser = Parser(schema, log_on_success=True)
    with StringChunkProvider(JSON_DICT) as provider:
        try:
            parser.parse(context, provider)
        except AllFailedToParseException as exc:
            print(exc)
            assert False


def parse_test(parse_tests: Sequence[ParseTest], parser: ChunkParser):
    for count, test in enumerate(parse_tests):
        chunk = Chunk(str(count), test.text)
        state, data = parser().parse(chunk, "origin", None)
        assert state == test.state
        assert data == test.data


def parse_test_fail(parse_tests: Sequence[ParseTest], parser: ChunkParser):
    for count, test in enumerate(parse_tests):
        chunk = Chunk(str(count), test.text)
        with pytest.raises(FailedParseException) as exc:
            _, _ = parser().parse(chunk, "origin", None)
            assert exc.state == "origin"  # type: ignore
            assert exc.parser is FailedParseException  # type: ignore
            assert exc.chunk == chunk  # type: ignore


def test_identier_parse():
    parse_tests: Sequence[ParseTest] = [
        ParseTest("foo = {\n", "identifier", {"identifier": "foo"})
    ]
    parse_test(parse_tests, IdentifierLine)


def test_identifier_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, IdentifierLine)


def test_empty_line_parse():
    parse_tests: Sequence[ParseTest] = [
        ParseTest("\n", "empty_line", {"whitespace": ""}),
        ParseTest("   \n", "empty_line", {"whitespace": "   "}),
    ]
    parse_test(parse_tests, EmptyLine)


def test_empty_line_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, EmptyLine)


def test_key_value_line():
    parse_tests: Sequence[ParseTest] = [
        ParseTest(
            '    "Name": "B. S. Johnson",\n',
            "key_value",
            {"key": "Name", "value": "B. S. Johnson"},
        )
    ]
    parse_test(parse_tests, KeyValueLine)


def test_key_value_line_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, KeyValueLine)


def test_key_list_line():
    parse_tests: Sequence[ParseTest] = [
        ParseTest(
            '    "Notable Creations": [\n', "key_list", {"key": "Notable Creations"}
        )
    ]
    parse_test(parse_tests, KeyListLine)


def test_key_list_line_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, KeyListLine)


def test_list_value_line():
    parse_tests: Sequence[ParseTest] = [
        ParseTest(
            """        "Archchancellor's Bathroom",\n""",
            "list_value",
            {"value": "Archchancellor's Bathroom"},
        )
    ]
    parse_test(parse_tests, ListValueLine)


def test_list_value_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, ListValueLine)


def test_list_end_line():
    parse_tests: Sequence[ParseTest] = [ParseTest("    ],\n", "list_end", {})]
    parse_test(parse_tests, ListEndLine)


def test_list_end_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, ListEndLine)


def test_dict_end_line():
    parse_tests: Sequence[ParseTest] = [ParseTest("}\n", "dict_end", {})]
    parse_test(parse_tests, DictEndLine)


def test_dict_end_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    parse_test_fail(parse_tests, DictEndLine)
