import re
from typing import Dict, Tuple

from pfmsoft.text_chunk_parser import Chunk, ChunkParser, ParseContext

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


class KeyValueLine(ChunkParser):
    def parse(
        self, chunk: Chunk, state: str, context: ParseContext
    ) -> Tuple[str, Dict]:
        regex = r"\s*\"(?P<key>[\w\s]+)\"\:\s*\"(?P<value>[\w\s.]+)\",\n"
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
        self, chunk: Chunk, state: str, context: ParseContext
    ) -> Tuple[str, Dict]:
        tokens = chunk.text.split()
        print(chunk)
        if (
            len(tokens) == 3
            and tokens[0].isidentifier()
            and tokens[1] == "="
            and tokens[2] == "{"
        ):
            return ("identifier", {"identifier": tokens[0], "terminus": tokens[2]})
        return self.report_parse_fail(chunk, state)


class EmptyLine(ChunkParser):
    def parse(
        self, chunk: Chunk, state: str, context: ParseContext
    ) -> Tuple[str, Dict]:
        regex = r"(?P<whitespace>[^\S\n]*)\n"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return ("empty_line", {"whitespace": match.group("whitespace")})
        return self.report_parse_fail(chunk, state)


def parse_schema():
    schema = {"origin": [IdentifierLine]}
    return schema
