import re
from typing import Dict, List, Sequence

from pfmsoft.text_chunk_parser import (
    Chunk,
    ChunkParser,
    EmptyLine,
    ParseResult,
    ParseResultHandler,
    ParseSchema,
)

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
# TODO option to not advance state
class JsonParseSchema(ParseSchema):
    def __init__(self):
        self.schema = {
            "origin": [EmptyLine(), IdentifierLine()],
            "empty_line": [IdentifierLine(), EmptyLine()],
            "identifier": [KeyValueLine()],
            "key_value": [KeyValueLine(), KeyListLine()],
            "key_list": [ListValueLine(), ListEndLine()],
            "list_value": [ListValueLine(), ListEndLine()],
            "list_end": [DictEndLine()],
            "dict_end": [EmptyLine()],
        }

    def expected(self, state: str) -> Sequence[ChunkParser]:
        parsers = self.schema.get(state, None)
        if parsers is None:
            raise NotImplementedError()
        return parsers


class JsonResultHandler(ParseResultHandler):
    # TODO implement parsed_data so that full behavior can be tested.
    #   Right now, success is verified by examining log output. Needs a round trip
    #   of the data to automate verification.
    def __init__(self, result_store: List) -> None:
        super().__init__()
        self.result_store = result_store

    def parsed_data(self, parse_result: ParseResult):
        """Handle the parsed data."""
        self.result_store.append(parse_result)


class DictEndLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^}\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        self.regex_match_or_fail(self.pattern, chunk, state)
        return ParseResult("dict_end", {}, self, chunk)


class ListEndLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\],\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        self.regex_match_or_fail(self.pattern, chunk, state)
        return ParseResult("list_end", {}, self, chunk)


class ListValueLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\"(?P<value>[\w\s'`\-]+)\",\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return ParseResult("list_value", {"value": match.group("value")}, self, chunk)


class KeyListLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\"(?P<key>[\w\s]+)\"\:\s*(?P<value>\[)\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return ParseResult("key_list", {"key": match.group("key")}, self, chunk)


class KeyValueLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\"(?P<key>[\w\s]+)\"\:\s*\"(?P<value>[\w\s.]+)\",\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return ParseResult(
            "key_value",
            {"key": match.group("key"), "value": match.group("value")},
            self,
            chunk,
        )


class IdentifierLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        tokens = chunk.text.split()
        if (
            len(tokens) == 3
            and tokens[0].isidentifier()
            and tokens[1] == "="
            and tokens[2] == "{"
        ):
            return ParseResult("identifier", {"identifier": tokens[0]}, self, chunk)
        return self.raise_parse_fail(None, chunk, state)
