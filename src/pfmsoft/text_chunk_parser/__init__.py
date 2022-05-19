"""Top-level package for text-chunk-parser."""
from pfmsoft.text_chunk_parser.chunk_parser import (
    AllFailedToParseException,
    Chunk,
    ChunkIterator,
    ChunkParser,
    EmptyLine,
    FailedParseException,
    Parser,
    ParseResult,
    ParseResultHandler,
    ParseSchema,
)

__author__ = """Chad Lowe"""
__email__ = "pfmsoft@gmail.com"
__version__ = "0.1.9"
