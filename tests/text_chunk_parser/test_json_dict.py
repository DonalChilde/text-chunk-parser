# pylint: disable=missing-docstring
import logging
import pprint
from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, List, Sequence

import pytest
from tests.text_chunk_parser.examples.json_dict import (
    JSON_DICT,
    DictEndLine,
    IdentifierLine,
    JsonParseSchema,
    JsonResultHandler,
    KeyListLine,
    KeyValueLine,
    ListEndLine,
    ListValueLine,
)

from pfmsoft.text_chunk_parser import (
    AllFailedToParseException,
    Chunk,
    ChunkIterator,
    ChunkParser,
    EmptyLine,
    FailedParseException,
    Parser,
    ParseResult,
)
from pfmsoft.text_chunk_parser.enumerated_filtered_iterator import Enumerated

pp = pprint.PrettyPrinter(indent=2)

# TODO check that schema actually parses
# TODO test various combinations of peek, history, and input size.


@dataclass
class ParseTest:
    text: str
    state: str
    data: Dict = field(default_factory=dict)


def test_parse_schema(caplog, logger: logging.Logger):
    caplog.set_level(logging.INFO)
    schema = JsonParseSchema()
    parser = Parser(schema, log_on_success=True)
    provider = ChunkIterator(StringIO(JSON_DICT), "Json Dict")
    results: List[ParseResult] = []
    with JsonResultHandler(results) as handler:
        try:
            parser.parse(handler, provider)
            pp.pprint(results)
        except AllFailedToParseException as exc:
            logger.info(exc)
            assert False
    # assert False


def parse_test(parse_tests: Sequence[ParseTest], source: str, parser: ChunkParser):
    for count, test in enumerate(parse_tests):
        chunk = Chunk(value=Enumerated(count, test.text), source=source)
        parse_result = parser().parse(chunk, "not_used")
        assert parse_result.new_state == test.state
        assert parse_result.data == test.data
        assert parse_result.chunk is chunk
        assert isinstance(parse_result.parser, parser)


def parse_test_fail(parse_tests: Sequence[ParseTest], source: str, parser: ChunkParser):
    for count, test in enumerate(parse_tests):
        chunk = Chunk(value=Enumerated(count, test.text), source=source)
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


def test_empty_chunk_parse():
    parse_tests: Sequence[ParseTest] = [
        ParseTest("\n", "empty_line", {"whitespace": ""}),
        ParseTest("   \n", "empty_line", {"whitespace": "   "}),
    ]
    source = __name__
    parse_test(parse_tests, source, EmptyLine)


def test_empty_chunk_parse_fail():
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
