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
    def parsed_data(self, chunk_parser: "ChunkParser", state, data):
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
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        regex = r"^}\n$"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return (
                "dict_end",
                {},
            )
        return self.report_parse_fail(chunk, state)


class ListEndLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        regex = r"^\s*\],\n$"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return (
                "list_end",
                {},
            )
        return self.report_parse_fail(chunk, state)


class ListValueLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        regex = r"^\s*\"(?P<value>[\w\s'`\-]+)\",\n$"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return (
                "list_value",
                {"value": match.group("value")},
            )
        return self.report_parse_fail(chunk, state)


class KeyListLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        regex = r"^\s*\"(?P<key>[\w\s]+)\"\:\s*(?P<value>\[)\n$"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return (
                "key_list",
                {"key": match.group("key")},
            )
        return self.report_parse_fail(chunk, state)


class KeyValueLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        regex = r"^\s*\"(?P<key>[\w\s]+)\"\:\s*\"(?P<value>[\w\s.]+)\",\n$"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return (
                "key_value",
                {"key": match.group("key"), "value": match.group("value")},
            )
        return self.report_parse_fail(chunk, state)


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
        return self.report_parse_fail(chunk, state)
