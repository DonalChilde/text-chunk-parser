"""Main module.

ChunkProvider - split_on - a regex string used to define a chunk boundry.
    keep_boundry_token :bool - whether to keep the boundry token in the chunk
    preview: int - how may chunks available for preview,
    history:int - how many parsed chunks to keep available for viewing.

    The ChunkProvider is an iterable that provides chunks of text.
    Start with a basic line reader with history and preview.
    Keep it simple. dont over think it.

Chunk - chunk_id: str - identifier for the chunk, eg. line number
    text: str - the text chunk.

ParseState - Enum? - defines parser state, ie. Alpha, start, ChunkId, end, omega

ChunkParser - callbacks:List[ParseCallback]?
    def parse(context,chunk,state)->ParseState,data Raises ParseException on failure.

ParseScheme - mapping of states to list of expected states

ParseContext - place to store parsed data, assimilate into whole, handle output.
    parsed_data(ChunkParser,state,data)

Parser parse_scheme, context
    def parse(ChunkProvider)
        state = "origin"
        for chunk in chunkprovider:
            for chunk_parser in parse_scheme[state]
                try:
                    state,data = chunk_parser.parse(context)
                    context.parsed_data(chunk_parser,state,data)
                    break
                except:
                    failed to parse, maybe log here
                all parsers failed to parse. big fail here


"""

import re
from io import StringIO
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

logger = getLogger(__name__)


class ChunkParserException(Exception):
    """Chunk parser exception base class"""


class FailedParseException(ChunkParserException):
    def __init__(
        self,
        msg: str | None,
        chunk: "Chunk",
        parser: "ChunkParser",
        state: str,
        **kwargs,
    ) -> None:
        if msg is None:
            msg = (
                f"\n\tFailed to parse chunk using {parser!r} parser."
                f"\n\tchunk: {chunk!r}"
                f"\n\tstate: {state}"
                f"\n\textra: {kwargs}"
            )
        super().__init__(msg)
        self.chunk = chunk
        self.parser = parser
        self.state = state
        self.kwargs = kwargs


class AllFailedToParseException(ChunkParserException):
    def __init__(
        self,
        msg: str | None,
        chunk: "Chunk",
        parsers: Sequence["ChunkParser"],
        state: str,
        **kwargs,
    ) -> None:
        if msg is None:
            msg = (
                f"\n\tAll parsers failed to parse chunk."
                f"\n\tparsers: {parsers!r}"
                f"\n\tchunk: {chunk}"
                f"\n\tstate: {state}"
                f"\n\textra: {kwargs}"
            )
        super().__init__(msg)
        self.chunk = chunk
        self.parsers = parsers
        self.state = state
        self.kwargs = kwargs


class Chunk:
    def __init__(self, chunk_id: str, text: str):
        self.chunk_id = chunk_id
        self.text = text

    def __repr__(self):
        return (
            f"{__class__.__name__}("
            f"chunk_id={self.chunk_id!r}, "
            f"text={self.text!r}"
            f")"
        )

    def __eq__(self, other):
        if not isinstance(other, Chunk):
            return False
        return self.chunk_id == other.chunk_id, self.text == other.text


class ChunkProvider:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class FileChunkProvider(ChunkProvider):
    def __init__(self, filepath: Path, encoding="utf-8"):
        self.filepath = filepath
        self.file_obj = open(filepath, mode="r", encoding=encoding)

    def __enter__(self):
        return self._read_chunk()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file_obj.close()

    def _read_chunk(self):
        count = 0
        for line in self.file_obj:
            count += 1
            yield Chunk(str(count), line)


class StringChunkProvider(ChunkProvider):
    def __init__(self, text: str):
        self.file_obj = StringIO(text)

    def __enter__(self):
        return self._read_chunk()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file_obj.close()

    def _read_chunk(self):
        count = 0
        for line in self.file_obj:
            count += 1
            yield Chunk(str(count), line)


class ParseContext:
    def parsed_data(self, chunk_parser: "ChunkParser", state, data):
        """Handle the parsed data."""
        raise NotImplementedError

    def initialize(self):
        """
        Do any work required to initialize the context.

        _extended_summary_
        """
        raise NotImplementedError

    def cleanup(self):
        """
        Do any work required to clean up after context

        """
        raise NotImplementedError


class ParseSchema:
    def expected(self, state: str) -> Sequence["ChunkParser"]:
        raise NotImplementedError


class ChunkParser:
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Any]:
        """returns a tuple of (state,data)"""
        raise NotImplementedError

    def report_parse_fail(self, chunk: Chunk, state: str, **kwargs):
        exc = FailedParseException(None, chunk, self, state, **kwargs)
        raise exc

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Parser:
    def __init__(
        self,
        schema: ParseSchema,
        log_on_success: bool = False,
        log_on_failure=True,
        exc_on_all_fail: bool = True,
    ):
        self.schema = schema
        self.log_on_success = log_on_success
        self.log_on_failure = log_on_failure
        self.exc_on_all_fail = exc_on_all_fail

    def _log_success(
        self, chunk: Chunk, chunk_parser: ChunkParser, state: str, data: Any
    ):
        if self.log_on_success:
            logger.info(
                "\n\tParsed chunk: %s with %r state: %s data: %s",
                chunk.chunk_id,
                chunk_parser,
                state,
                data,
            )

    def _log_failure(self, exc: FailedParseException):
        if self.log_on_failure:
            logger.info(exc)

    def _attempt_parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
        parsers: Sequence[ChunkParser],
    ):
        for chunk_parser in parsers:
            try:
                new_state, data = chunk_parser.parse(chunk, state, context)
                context.parsed_data(chunk_parser, new_state, data)
                self._log_success(chunk, chunk_parser, new_state, data)
                return new_state
            except FailedParseException as exc:
                self._log_failure(exc)
                continue
        logger.info(
            (
                "All parsers failed to parse chunk.\nChunk: %s\n"
                "parsers: %r\nstate: %s"
            ),
            chunk,
            parsers,
            state,
        )
        if self.exc_on_all_fail:
            raise AllFailedToParseException(None, chunk, parsers, state)

    def parse(
        self,
        context: ParseContext,
        chunk_provider: Iterable,
    ):
        state = "origin"
        context.initialize()
        for chunk in chunk_provider:
            new_state = self._attempt_parse(
                chunk,
                state,
                context,
                self.schema.expected(state),
            )
            state = new_state
        context.cleanup()


class EmptyLine(ChunkParser):
    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        regex = r"(?P<whitespace>[^\S\n]*)\n"
        pattern = re.compile(regex)
        match = pattern.match(chunk.text)
        if match:
            return ("empty_line", {"whitespace": match.group("whitespace")})
        return self.report_parse_fail(chunk, state)
