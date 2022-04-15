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
    with StringChunkProvider("Json Dict", JSON_DICT) as provider:
        try:
            parser.parse(context, provider)
        except AllFailedToParseException as exc:
            print(exc)
            assert False


def parse_test(parse_tests: Sequence[ParseTest], source: str, parser: ChunkParser):
    for count, test in enumerate(parse_tests):
        chunk = Chunk(str(count), source, test.text)
        state, data = parser().parse(chunk, "origin", None)
        assert state == test.state
        assert data == test.data


def parse_test_fail(parse_tests: Sequence[ParseTest], source: str, parser: ChunkParser):
    for count, test in enumerate(parse_tests):
        chunk = Chunk(str(count), source, test.text)
        with pytest.raises(FailedParseException) as exc:
            _, _ = parser().parse(chunk, "origin", None)
            assert exc.state == "origin"  # type: ignore
            assert exc.parser is FailedParseException  # type: ignore
            assert exc.chunk == chunk  # type: ignore


def test_identier_parse():
    parse_tests: Sequence[ParseTest] = [
        ParseTest("foo = {\n", "identifier", {"identifier": "foo"})
    ]
    source = __name__
    parse_test(parse_tests, source, IdentifierLine)


def test_identifier_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, IdentifierLine)


def test_empty_line_parse():
    parse_tests: Sequence[ParseTest] = [
        ParseTest("\n", "empty_line", {"whitespace": ""}),
        ParseTest("   \n", "empty_line", {"whitespace": "   "}),
    ]
    source = __name__
    parse_test(parse_tests, source, EmptyLine)


def test_empty_line_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, EmptyLine)


def test_key_value_line():
    parse_tests: Sequence[ParseTest] = [
        ParseTest(
            '    "Name": "B. S. Johnson",\n',
            "key_value",
            {"key": "Name", "value": "B. S. Johnson"},
        )
    ]
    source = __name__
    parse_test(parse_tests, source, KeyValueLine)


def test_key_value_line_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, KeyValueLine)


def test_key_list_line():
    parse_tests: Sequence[ParseTest] = [
        ParseTest(
            '    "Notable Creations": [\n', "key_list", {"key": "Notable Creations"}
        )
    ]
    source = __name__
    parse_test(parse_tests, source, KeyListLine)


def test_key_list_line_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, KeyListLine)


def test_list_value_line():
    parse_tests: Sequence[ParseTest] = [
        ParseTest(
            """        "Archchancellor's Bathroom",\n""",
            "list_value",
            {"value": "Archchancellor's Bathroom"},
        )
    ]
    source = __name__
    parse_test(parse_tests, source, ListValueLine)


def test_list_value_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, ListValueLine)


def test_list_end_line():
    parse_tests: Sequence[ParseTest] = [ParseTest("    ],\n", "list_end", {})]
    source = __name__
    parse_test(parse_tests, source, ListEndLine)


def test_list_end_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, ListEndLine)


def test_dict_end_line():
    parse_tests: Sequence[ParseTest] = [ParseTest("}\n", "dict_end", {})]
    source = __name__
    parse_test(parse_tests, source, DictEndLine)


def test_dict_end_parse_fail():
    parse_tests: Sequence[ParseTest] = [ParseTest("  bad value  ],\n", "list_end", {})]
    source = __name__
    parse_test_fail(parse_tests, source, DictEndLine)
