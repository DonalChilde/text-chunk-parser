import re
from typing import Dict, Sequence, Tuple

from pfmsoft.text_chunk_parser import Chunk, ChunkParser, ParseContext, ParseSchema
from pfmsoft.text_chunk_parser.text_chunk_parser import EmptyLine

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


class JsonParseContext(ParseContext):
    def parsed_data(self, state, data):
        """Handle the parsed data."""
        pass

    def initialize(self):
        """
        Do any work required to initialize the context.

        _extended_summary_
        """

    def cleanup(self):
        """
        Do any work required to clean up after context

        """


class DictEndLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^}\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        self.regex_match_or_fail(self.pattern, chunk, state)
        return (
            "dict_end",
            {},
        )


class ListEndLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\],\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        self.regex_match_or_fail(self.pattern, chunk, state)
        return (
            "list_end",
            {},
        )


class ListValueLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\"(?P<value>[\w\s'`\-]+)\",\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return (
            "list_value",
            {"value": match.group("value")},
        )


class KeyListLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\"(?P<key>[\w\s]+)\"\:\s*(?P<value>\[)\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return (
            "key_list",
            {"key": match.group("key")},
        )


class KeyValueLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^\s*\"(?P<key>[\w\s]+)\"\:\s*\"(?P<value>[\w\s.]+)\",\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return (
            "key_value",
            {"key": match.group("key"), "value": match.group("value")},
        )


class IdentifierLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        tokens = chunk.text.split()
        if (
            len(tokens) == 3
            and tokens[0].isidentifier()
            and tokens[1] == "="
            and tokens[2] == "{"
        ):
            return ("identifier", {"identifier": tokens[0]})
        return self.report_parse_fail(None, chunk, state)
