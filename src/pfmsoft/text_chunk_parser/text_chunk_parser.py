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
from logging import NullHandler, getLogger
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class ChunkParserException(Exception):
    """Chunk parser exception base class"""


class FailedParseException(ChunkParserException):
    def __init__(
        self,
        msg: str | None,
        reason: str | None,
        chunk: "Chunk",
        parser: "ChunkParser",
        state: str,
        **kwargs,
    ) -> None:
        if msg is None:
            msg = (
                f"Failed to parse chunk {chunk.chunk_id} using {parser!r} parser."
                f"\n\treason: {reason}"
                f"\n\tchunk: {chunk!r}"
                f"\n\tcurrent state: {state}"
            )
        super().__init__(msg)
        self.reason = reason
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
        excs: Sequence[FailedParseException] | None = None,
        **kwargs,
    ) -> None:
        if excs is None:
            self.excs: Sequence[FailedParseException] = []
        else:
            self.excs = excs
        if msg is None:
            msg = (
                f"{parsers!r} failed to parse chunk."
                f"\n\tchunk: {chunk!r}"
                f"\n\tstate: {state}"
            )
            reasons = [f"\n\t{exc.parser!r}: {exc.reason}" for exc in excs]  # type: ignore
            msg = msg + "".join(reasons)

        super().__init__(msg)
        self.chunk = chunk
        self.parsers = parsers
        self.state = state
        self.kwargs = kwargs


class Chunk:
    def __init__(self, chunk_id: str, source: str, text: str):
        self.chunk_id = chunk_id
        self.source = source
        self.text = text

    def __repr__(self):
        return (
            f"{__class__.__name__}("
            f"chunk_id={self.chunk_id!r}, "
            f"source={self.source!r}, "
            f"text={self.text!r}"
            f")"
        )

    def __eq__(self, other):
        if not isinstance(other, Chunk):
            return False
        return self.chunk_id == other.chunk_id, self.text == other.text

    def _debug_print(self):
        # TODO make a useful debug print string, expect to have next/prev tuples.
        raise NotImplementedError()


class ChunkExpanded(Chunk):
    def __init__(self, chunk_id: str, source: str, text: str):
        super().__init__(chunk_id=chunk_id, source=source, text=text)
        self.previous: Sequence[Tuple[int, str]] = []
        self.following: Sequence[Tuple[int, str]] = []
        # FIXME make history/peek a standard chunk ability.

    def __repr__(self):
        return (
            f"{__class__.__name__}("
            f"chunk_id={self.chunk_id!r}, "
            f"source={self.source!r}, "
            f"text={self.text!r}"
            f")"
        )

    def __eq__(self, other):
        if not isinstance(other, Chunk):
            return False
        return self.chunk_id == other.chunk_id, self.text == other.text


class ChunkProvider:
    """
    _summary_

    _extended_summary_
    TODO keep internal next/previous limited list of raw chunks. add as
        tuple to Chunk to support look ahead/look back and better debug messages.
    """

    def __init__(self, source_name: str, skip_empty_chunks: bool = True):
        self.source_name = source_name
        self.skip_empty_chunks = skip_empty_chunks
        regex = r"^(?P<whitespace>[^\S\n]*)\n$"
        self.empty_line_pattern = re.compile(regex)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def log_empty_line(self, source_name: str, line_number: int):
        logger.info(
            "%s skipping blank line %s from %s",
            self.__class__.__name__,
            line_number,
            source_name,
        )

    def _check_for_skip(self, text: str, count: int) -> bool:
        if self.skip_empty_chunks:
            match = self.empty_line_pattern.match(text)
            if match:
                self.log_empty_line(self.source_name, count)
                return True
        return False


class FileChunkProvider(ChunkProvider):
    def __init__(
        self,
        source_name: str,
        filepath: Path,
        skip_empty_chunks: bool = True,
        encoding="utf-8",
    ):
        super().__init__(source_name=source_name, skip_empty_chunks=skip_empty_chunks)
        self.filepath = filepath
        # FIXME move file open to __enter__?
        self.file_obj = open(filepath, mode="r", encoding=encoding)

    def __enter__(self):
        return self._read_chunk()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file_obj.close()

    def _read_chunk(self):
        count = 0
        for line in self.file_obj:
            count += 1
            if self._check_for_skip(line, count):
                continue
            yield Chunk(str(count), self.source_name, line)


class StringChunkProvider(ChunkProvider):
    def __init__(self, source_name: str, text: str, skip_empty_chunks: bool = True):
        super().__init__(source_name=source_name, skip_empty_chunks=skip_empty_chunks)
        self.file_obj = StringIO(text)

    def __enter__(self):
        return self._read_chunk()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file_obj.close()

    def _read_chunk(self):
        count = 0
        for line in self.file_obj:
            count += 1
            if self._check_for_skip(line, count):
                continue
            yield Chunk(str(count), self.source_name, line)


class ParseContext:
    def parsed_data(self, state: str, data: Any, chunk: Chunk, parser: "ChunkParser"):
        """Handle the parsed data. Check for SkipChunk, means ignore data and state"""
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

    def raise_parse_fail(
        self,
        reason: str | None,
        chunk: Chunk,
        state: str,
        exc: Exception | None = None,
        **kwargs,
    ):
        fail_exc = FailedParseException(None, reason, chunk, self, state, **kwargs)
        if exc:
            raise fail_exc from exc
        raise fail_exc

    def regex_match_or_fail(self, pattern: re.Pattern, chunk: Chunk, state: str):
        match = pattern.match(chunk.text)
        if match:
            return match
        reason = f"Regex pattern {pattern.pattern!r} failed to match text."
        self.raise_parse_fail(reason, chunk, state, regex=pattern.pattern)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Parser:
    def __init__(
        self,
        schema: ParseSchema,
        log_on_success: bool = False,
    ):
        self.schema = schema
        self.log_on_success = log_on_success

    def _log_success(
        self, chunk: Chunk, chunk_parser: ChunkParser, state: str, data: Any
    ):
        if self.log_on_success:
            logger.info(
                "Parse successful.\n"
                "\tchunk: %r\n"
                "\tparser: %r\n"
                "\tResulting parser state: %r\n"
                "\tParsed data: %r",
                chunk,
                chunk_parser,
                state,
                data,
            )

    def _attempt_parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
        parsers: Sequence[ChunkParser],
    ) -> Tuple[str, Any, ChunkParser]:

        fail_excs: List[FailedParseException] = []
        for chunk_parser in parsers:
            try:
                new_state, data = chunk_parser.parse(chunk, state, context)
                self._log_success(chunk, chunk_parser, new_state, data)
                return new_state, data, chunk_parser
            except FailedParseException as exc:
                fail_excs.append(exc)
                logger.info(exc)
                continue
        raised_exc = AllFailedToParseException(None, chunk, parsers, state, fail_excs)
        logger.info(raised_exc)
        raise raised_exc

    def parse(
        self,
        context: ParseContext,
        chunk_provider: Iterable,
    ):
        state = "origin"
        context.initialize()
        for chunk in chunk_provider:
            new_state, data, parser = self._attempt_parse(
                chunk,
                state,
                context,
                self.schema.expected(state),
            )
            state = new_state
            context.parsed_data(new_state, data, chunk, parser)
        context.cleanup()


# TODO refactor to EmptyChunk
class EmptyLine(ChunkParser):
    def __init__(self) -> None:
        regex = r"^(?P<whitespace>[^\S\n]*)\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return ("empty_line", {"whitespace": match.group("whitespace")})


class SkipChunk(ChunkParser):
    def __init__(self) -> None:
        pass

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:

        return (state, {})
