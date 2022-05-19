# -*- coding: utf-8 -*-
#
#  chunk_parser.py
#  _project_
#
#  Created by Chad Lowe on 2022-05-19.
#  Copyright 2022 Chad Lowe. All rights reserved.
#

import re
from dataclasses import dataclass
from logging import NullHandler, getLogger
from typing import Any, Dict, List, Sequence

from pfmsoft.text_chunk_parser.chunk_iterator import Chunk, ChunkIterator

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class ChunkParserException(Exception):
    """Chunk parser exception base class"""


class FailedParseException(ChunkParserException):
    """
    The exception raised when a chunk fails to parse with an individual parser.
    """

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
                f"Failed to parse chunk {chunk.count} using {parser!r} parser."
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
    """
    The exception raised when all parsers in the parse schema fail to parse a chunk.
    """

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


class ParseResultHandler:
    """
    The ParseResultHandler handles what to do with the parsed data. Subclass this with the
    specific behavior required.
    """

    def __init__(self, **kwargs) -> None:
        pass

    def parsed_data(self, parse_result: "ParseResult"):
        """Handle the parsed data. Called after each successful parse."""
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def parse_hints(self) -> Dict:
        """
        Override this to provide parse hints that will be passed for each parse attempt.
        Hints can be updated by ParseContext as needed to reflect the current state.
        """
        return {}


class ParseSchema:
    """
    Provides the specific parse scheme.
    """

    def expected(self, state: str) -> Sequence["ChunkParser"]:
        """
        Return a sequence of `ChunkParser` expected to match the next `Chunk`.

        Args:
            state: The current state of the parse.

        Returns:
            A sequence of parsers expected to match the next Chunk.

        """
        raise NotImplementedError


@dataclass
class ParseResult:
    """
    The successful parse result from ChunkParser.parse

    Args:
        new_state: The new state of the parser.
        data: Any data parsed from the chunk.
        parser: The parser used to parse the chunk.
        chunk: The chunk parsed.
    """

    new_state: str
    data: Any
    parser: "ChunkParser"
    chunk: Chunk


class ChunkParser:
    """
    Base class for a ChunkParser
    """

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        """
        Override with the code for parsing a specific Chunk.

        If the parse fails, must call self.raise_parse_fail(), or raise a FailedParseException.

        If the parse succedes must return ParseResult.

        Args:
            chunk: The chunk to be parsed.
            state: The current state of the parser.
            parse_hints: Optional dict with values from ParseContext that may be
                required for a successful parse. Defaults to None.

        Returns:
            The result of a successful parse.
        """
        raise NotImplementedError

    def raise_parse_fail(
        self,
        reason: str | None,
        chunk: Chunk,
        state: str,
        exc: Exception | None = None,
        **kwargs,
    ):
        """
        Builds and raises a FailedParseException.
        """
        fail_exc = FailedParseException(None, reason, chunk, self, state, **kwargs)
        if exc:
            raise fail_exc from exc
        raise fail_exc

    def regex_match_or_fail(self, pattern: re.Pattern, chunk: Chunk, state: str):
        """
        Convenience function for regex parsing.
        """
        match = pattern.match(chunk.text)
        if match:
            return match
        reason = f"Regex pattern {pattern.pattern!r} failed to match text."
        self.raise_parse_fail(reason, chunk, state, regex=pattern.pattern)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Parser:
    """
    Parser.parse handles calling the parsers for each chunk.
    """

    def __init__(
        self,
        schema: ParseSchema,
        log_on_success: bool = False,
    ):
        """

        Args:
            schema: The schema for a parse job.
            log_on_success: Log successful parses. Defaults to False.
        """
        self.schema = schema
        self.log_on_success = log_on_success

    def _log_success(self, parse_result: ParseResult):
        if self.log_on_success:
            logger.info(
                "Parse successful.\n"
                "\tchunk: %s\n"
                "\tparser: %r\n"
                "\tResulting parser state: %r\n"
                "\tParsed data: %r",
                parse_result.chunk,
                parse_result.parser,
                parse_result.new_state,
                parse_result.data,
            )

    def _attempt_parse(
        self,
        chunk: Chunk,
        state: str,
        handler: ParseResultHandler,
        parsers: Sequence[ChunkParser],
    ) -> ParseResult:

        failed_parse_exceptions: List[FailedParseException] = []
        for chunk_parser in parsers:
            try:
                parse_return = chunk_parser.parse(chunk, state, handler.parse_hints())
                self._log_success(parse_return)
                return parse_return
            except FailedParseException as exc:
                failed_parse_exceptions.append(exc)
                logger.info(exc)
                continue
        raised_exc = AllFailedToParseException(
            None, chunk, parsers, state, failed_parse_exceptions
        )
        logger.warning(raised_exc)
        raise raised_exc

    def parse(
        self,
        handler: ParseResultHandler,
        chunk_provider: ChunkIterator,
    ):
        """
        Parse data from text.

        Parse the text chunks from chunk_provider. The resulting data is handled in the
        `ParseResultHandler`.

        Args:
            handler: The parse handler for an individual parsing job.
            chunk_provider: An iterator that provides the Chunks to be parsed.

        """
        state = "origin"
        for chunk in chunk_provider:
            parse_return = self._attempt_parse(
                chunk,
                state,
                handler,
                self.schema.expected(state),
            )
            state = parse_return.new_state
            handler.parsed_data(parse_return)


class EmptyLine(ChunkParser):
    """
    An example of a regex parser that will match an empty line.
    """

    def __init__(self) -> None:
        regex = r"^(?P<whitespace>[^\S\n]*)\n$"
        self.pattern = re.compile(regex)

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        _ = parse_hints
        match = self.regex_match_or_fail(self.pattern, chunk, state)
        return ParseResult(
            new_state="empty_line",
            data={"whitespace": match.group("whitespace")},
            chunk=chunk,
            parser=self,
        )


class SkipChunk(ChunkParser):
    """
    A parser that will skip a chunk without advancing the state.
    """

    def __init__(self) -> None:
        pass

    def parse(
        self,
        chunk: Chunk,
        state: str,
        parse_hints: Dict | None = None,
    ) -> ParseResult:
        _ = parse_hints
        return ParseResult(state, {}, self, chunk)
