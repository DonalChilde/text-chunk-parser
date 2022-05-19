# # -*- coding: utf-8 -*-
# #
# #  text_chunk_parser.py
# #
# #
# #  Created by Chad Lowe on 2022-05-18.
# #  Copyright 2022 Chad Lowe. All rights reserved.
# #


# """Use this framework to parse chunks of data.

# text_chunk_parser allows you to define a parse scheme that uses "state" to predict the
# required parser for the next chunk of text. Each successful parse can update the "state"
# value predicting the parser for the following chunk of text.

# Describe the data you expect to parse:

# Subclass ChunkParser to define a parser for each type of text chunk. The parser parses any
# data in the chunk, and determines the new state of the parse.

# Subclass ParseScheme as the provider of a list of possible parsers based on the current
# "state" of the parse. A Dict[str,List[ChunkParser]] is easily used to contain the parse
# scheme structure, with the key being the current "state" of the parse. "origin" is used
# as the "state" key representing the start of a parse. "origin" must be present as a key
# in every parse scheme.

# Subclass ParseContext as the recipient of the data from successful parses. ParseContext
# handles storing and any further manipulation of the data from parses. It can also provide
# parse_hints to the parser that can contain any additional info to assist in a successful
# parse.

# ChunkIterator will "chunk" a text iterable, creating `Chunk`s that contain the current
# text, as well as a configurable number of "peeks" into future values, and past values.

# Usage:

#     schema = JsonParseSchema()
#     parser = Parser(schema, log_on_success=True)
#     chunk_iterator = ChunkIterator(StringIO(JSON_DICT), "Json Dict")
#     results: List[ParseResult] = []
#     with JsonResultHandler(results) as handler:
#         try:
#             parser.parse(handler, chunk_iterator)
#         except AllFailedToParseException as exc:
#             logger.warning(exc)
#             raise exc


# """


# import re
# from collections import deque
# from dataclasses import dataclass
# from itertools import chain
# from logging import NullHandler, getLogger
# from typing import Any, Callable, Deque, Dict, Iterable, Iterator, List, Sequence, Tuple

# logger = getLogger(__name__)
# logger.addHandler(NullHandler())


# class ChunkParserException(Exception):
#     """Chunk parser exception base class"""


# class FailedParseException(ChunkParserException):
#     """
#     The exception raised when a chunk fails to parse with an individual parser.
#     """

#     def __init__(
#         self,
#         msg: str | None,
#         reason: str | None,
#         chunk: "Chunk",
#         parser: "ChunkParser",
#         state: str,
#         **kwargs,
#     ) -> None:
#         if msg is None:
#             msg = (
#                 f"Failed to parse chunk {chunk.morsel.ident} using {parser!r} parser."
#                 f"\n\treason: {reason}"
#                 f"\n\tchunk: {chunk!r}"
#                 f"\n\tcurrent state: {state}"
#             )
#         super().__init__(msg)
#         self.reason = reason
#         self.chunk = chunk
#         self.parser = parser
#         self.state = state
#         self.kwargs = kwargs


# class AllFailedToParseException(ChunkParserException):
#     """
#     The exception raised when all parsers in the parse schema fail to parse a chunk.
#     """

#     def __init__(
#         self,
#         msg: str | None,
#         chunk: "Chunk",
#         parsers: Sequence["ChunkParser"],
#         state: str,
#         excs: Sequence[FailedParseException] | None = None,
#         **kwargs,
#     ) -> None:
#         if excs is None:
#             self.excs: Sequence[FailedParseException] = []
#         else:
#             self.excs = excs
#         if msg is None:
#             msg = (
#                 f"{parsers!r} failed to parse chunk."
#                 f"\n\tchunk: {chunk!r}"
#                 f"\n\tstate: {state}"
#             )
#             reasons = [f"\n\t{exc.parser!r}: {exc.reason}" for exc in excs]  # type: ignore
#             msg = msg + "".join(reasons)

#         super().__init__(msg)
#         self.chunk = chunk
#         self.parsers = parsers
#         self.state = state
#         self.kwargs = kwargs


# @dataclass
# class Morsel:
#     """
#     The smallest unit of input, a section of text with an identifier,
#     e.g. line number, and line of text.

#     """

#     ident: str
#     text: str

#     def __str__(self):
#         return f"{self.ident}: {self.text!r}"


# class Chunk:
#     """
#     The object sent to the parser, containing the current Morsel, as well as
#     an amount of past morsels, and a peek into future Morsels. Access the current
#     Morsel through self.morsel.

#     # TODO make __get_index__
#         0 == self.morsel()
#         -1 == next future morsel
#         1 == most recent past morsel
#     # TODO make morsel a property.
#     """

#     def __init__(
#         self,
#         morsel: Morsel,
#         peek: Tuple[Morsel, ...] = (),
#         past: Tuple[Morsel, ...] = (),
#         source: str = "",
#     ):
#         self.morsel = morsel
#         self.peek = peek
#         self.past = past
#         self.source = source

#     def __str__(self):
#         return (
#             f"{__class__.__name__}(" f"{self.morsel}, " f"source={self.source!r}" f")"
#         )

#     # def verbose_str(self):
#     #     """
#     #     A verbose string output of the entire Chunk, useful for debugging.
#     #     """
#     #     cached_string = []
#     #     current_index = self.current_index
#     #     for morsel in self.data:
#     #         cached_string.append(f"[{current_index}] {morsel!s}")
#     #         current_index -= 1
#     #     return "\n".join(cached_string)

#     def __repr__(self):
#         return (
#             f"{__class__.__name__}("
#             f"morsel={self.morsel}, "
#             f"peek={self.peek}, "
#             f"past={self.past}, "
#             f"source={self.source!r}, "
#             f")"
#         )


# def skip_blank_lines(morsel: Morsel, source: str = "") -> bool:
#     """
#     An example of a filter function that can be used with ChunkIterator.
#     This function will skip blank lines.
#     """
#     regex = r"^(?P<whitespace>[^\S\n]*)\n$"
#     empty_line_pattern = re.compile(regex)
#     match = empty_line_pattern.match(morsel.text)
#     if match:
#         logger.info(
#             "Skipping blank line %s from %s",
#             morsel.ident,
#             source,
#         )
#         return True
#     return False


# class PlaceHolder:
#     pass


# class ChunkIterator:
#     """
#     Convert a text iterator to a Chunk iterator.

#     ChunkIterator provides peek and history for a text iterator in the provided Chunk.
#     `Chunk`s contain a tuple of Morsels representing the current Morsel, along with
#     peek and history. The Morsels have the iteration count as a string in the Morsel.ident
#     property, and the text in the Morsel.text property.

#     Iteration count is maintained even if chunks are skipped through the chunk_filter function.


#     """

#     def __init__(
#         self,
#         iterable: Iterator,
#         source: str = "",
#         chunk_filter: Callable[[Morsel, str], bool] | None = skip_blank_lines,
#         history_size: int = 3,
#         peek_size: int = 3,
#     ):
#         """
#         Args:
#             iterable: Iterable source of text to be chunked.
#             source: The name of the source. Defaults to "".
#             chunk_filter: A filter function that can be used to skip chunks of text.
#                 Defaults to skip_blank_lines.
#             history_size: The size of the history buffer. Defaults to 3.
#             peek_size: The size of the peek buffer. Minimum 1. Defaults to 3.
#         """
#         self.iterable = iterable
#         self.source = source
#         self.history_size = history_size
#         self.peek_size = max(peek_size, 1)
#         self.peek: Deque[Morsel] = deque(maxlen=peek_size)
#         self.history: Deque[Morsel] = deque(maxlen=history_size)
#         self.current: Morsel | PlaceHolder = PlaceHolder()
#         self.chunk_filter = chunk_filter
#         self.count = 0
#         self.current_index = peek_size
#         self.initialized: bool = False

#     def _skip_chunk(self, morsel: Morsel) -> bool:
#         if self.chunk_filter:
#             return self.chunk_filter(morsel, self.source)
#         return False

#     def _read_chunk(self) -> Chunk:
#         try:
#             self._check_initialized()
#             if isinstance(self.current, PlaceHolder):
#                 self.current = self.peek.popleft()
#                 next_morsel = self._next_morsel()
#                 self.peek.append(next_morsel)
#                 return self._make_chunk()
#                 # TODO Stoppedhere
#             # morsel = self._make_morsel()
#             # if not self._skip_chunk(morsel):
#             #     value = self.peek.pop()
#             #     self.peek.appendleft(morsel)
#             #     self.history.appendleft(value)
#             next_morsel = self._next_morsel()

#             return Chunk(
#                 tuple(chain(self.peek, self.history)), self.source, len(self.peek)
#             )
#         except StopIteration as exc:
#             if self.peek:
#                 morsel = self.peek.pop()
#                 self.history.appendleft(morsel)
#                 return Chunk(
#                     tuple(chain(self.peek, self.history)), self.source, len(self.peek)
#                 )
#             raise StopIteration from exc

#     def _make_chunk(self) -> Chunk:
#         return Chunk(
#             morsel=self.current,
#             peek=tuple(self.peek),
#             past=tuple(self.history),
#             source=self.source,
#         )

#     def _next_morsel(self) -> Morsel:
#         """Get the next filtered Morsel."""
#         while True:
#             morsel = self._make_morsel()
#             if not self._skip_chunk(morsel):
#                 return morsel

#     def _make_morsel(self) -> Morsel:
#         """Get the next item from iterable and make a Morsel."""
#         text = next(self.iterable)
#         self.count += 1
#         morsel = Morsel(str(self.count), text)
#         return morsel

#     def _check_initialized(self):
#         """Fill the peek queue on first access of iterator."""
#         if not self.initialized and self.peek_size > 0:
#             while len(self.peek) < self.peek_size:
#                 # morsel = self._make_morsel()
#                 # if not self._skip_chunk(morsel):
#                 #     self.peek.appendleft(morsel)
#                 morsel = self._next_morsel()
#                 self.peek.append(morsel)
#             self.initialized = True

#     def __iter__(self):
#         return self

#     def __next__(self):
#         return self._read_chunk()


# class ParseResultHandler:
#     """
#     The ParseResultHandler handles what to do with the parsed data. Subclass this with the
#     specific behavior required.
#     """

#     def __init__(self, **kwargs) -> None:
#         pass

#     def parsed_data(self, parse_result: "ParseResult"):
#         """Handle the parsed data. Called after each successful parse."""
#         raise NotImplementedError

#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         pass

#     # def initialize(self):
#     #     """
#     #     Do any work required to initialize the context. Called at the beginning of
#     #     Parser.parse()

#     #     """
#     #     raise NotImplementedError

#     # def cleanup(self):
#     #     """
#     #     Do any work required to clean up after context. Called at the end of
#     #     Parser.parse()

#     #     """
#     #     raise NotImplementedError

#     def parse_hints(self) -> Dict:
#         """
#         Override this to provide parse hints that will be passed for each parse attempt.
#         Hints can be updated by ParseContext as needed to reflect the current state.
#         """
#         return {}


# class ParseSchema:
#     """
#     Provides the specific parse scheme.
#     """

#     def expected(self, state: str) -> Sequence["ChunkParser"]:
#         """
#         Return a sequence of `ChunkParser` expected to match the next `Chunk`.

#         Args:
#             state: The current state of the parse.

#         Returns:
#             A sequence of parsers expected to match the next Chunk.

#         """
#         raise NotImplementedError


# @dataclass
# class ParseResult:
#     """
#     The successful parse result from ChunkParser.parse

#     Args:
#         new_state: The new state of the parser.
#         data: Any data parsed from the chunk.
#         parser: The parser used to parse the chunk.
#         chunk: The chunk parsed.
#     """

#     new_state: str
#     data: Any
#     parser: "ChunkParser"
#     chunk: Chunk


# class ChunkParser:
#     """
#     Base class for a ChunkParser
#     """

#     def parse(
#         self,
#         chunk: Chunk,
#         state: str,
#         parse_hints: Dict | None = None,
#     ) -> ParseResult:
#         """
#         Override with the code for parsing a specific Chunk.

#         If the parse fails, must call self.raise_parse_fail(), or raise a FailedParseException.

#         If the parse succedes must return ParseResult.

#         Args:
#             chunk: The chunk to be parsed.
#             state: The current state of the parser.
#             parse_hints: Optional dict with values from ParseContext that may be
#                 required for a successful parse. Defaults to None.

#         Returns:
#             The result of a successful parse.
#         """
#         raise NotImplementedError

#     def raise_parse_fail(
#         self,
#         reason: str | None,
#         chunk: Chunk,
#         state: str,
#         exc: Exception | None = None,
#         **kwargs,
#     ):
#         """
#         Builds and raises a FailedParseException.
#         """
#         fail_exc = FailedParseException(None, reason, chunk, self, state, **kwargs)
#         if exc:
#             raise fail_exc from exc
#         raise fail_exc

#     def regex_match_or_fail(self, pattern: re.Pattern, chunk: Chunk, state: str):
#         """
#         Convenience function for regex parsing.
#         """
#         match = pattern.match(chunk.morsel().text)
#         if match:
#             return match
#         reason = f"Regex pattern {pattern.pattern!r} failed to match text."
#         self.raise_parse_fail(reason, chunk, state, regex=pattern.pattern)

#     def __repr__(self):
#         return f"{self.__class__.__name__}()"


# class Parser:
#     """
#     Parser.parse handles calling the parsers for each chunk.
#     """

#     def __init__(
#         self,
#         schema: ParseSchema,
#         log_on_success: bool = False,
#     ):
#         """

#         Args:
#             schema: The schema for a parse job.
#             log_on_success: Log successful parses. Defaults to False.
#         """
#         self.schema = schema
#         self.log_on_success = log_on_success

#     def _log_success(self, parse_result: ParseResult):
#         if self.log_on_success:
#             logger.info(
#                 "Parse successful.\n"
#                 "\tchunk: %s\n"
#                 "\tparser: %r\n"
#                 "\tResulting parser state: %r\n"
#                 "\tParsed data: %r",
#                 parse_result.chunk,
#                 parse_result.parser,
#                 parse_result.new_state,
#                 parse_result.data,
#             )

#     def _attempt_parse(
#         self,
#         chunk: Chunk,
#         state: str,
#         handler: ParseResultHandler,
#         parsers: Sequence[ChunkParser],
#     ) -> ParseResult:

#         failed_parse_exceptions: List[FailedParseException] = []
#         for chunk_parser in parsers:
#             try:
#                 parse_return = chunk_parser.parse(chunk, state, handler.parse_hints())
#                 self._log_success(parse_return)
#                 return parse_return
#             except FailedParseException as exc:
#                 failed_parse_exceptions.append(exc)
#                 logger.info(exc)
#                 continue
#         raised_exc = AllFailedToParseException(
#             None, chunk, parsers, state, failed_parse_exceptions
#         )
#         logger.warning(raised_exc)
#         raise raised_exc

#     def parse(
#         self,
#         handler: ParseResultHandler,
#         chunk_provider: Iterable,
#     ):
#         """
#         Parse data from text.

#         Parse the text chunks from chunk_provider. The resulting data is handled in the
#         `ParseResultHandler`.

#         Args:
#             handler: The parse handler for an individual parsing job.
#             chunk_provider: An iterator that provides the Chunks to be parsed.

#         """
#         state = "origin"
#         for chunk in chunk_provider:
#             parse_return = self._attempt_parse(
#                 chunk,
#                 state,
#                 handler,
#                 self.schema.expected(state),
#             )
#             state = parse_return.new_state
#             handler.parsed_data(parse_return)


# class EmptyLine(ChunkParser):
#     """
#     An example of a regex parser that will match an empty line.
#     """

#     def __init__(self) -> None:
#         regex = r"^(?P<whitespace>[^\S\n]*)\n$"
#         self.pattern = re.compile(regex)

#     def parse(
#         self,
#         chunk: Chunk,
#         state: str,
#         parse_hints: Dict | None = None,
#     ) -> ParseResult:
#         _ = parse_hints
#         match = self.regex_match_or_fail(self.pattern, chunk, state)
#         return ParseResult(
#             new_state="empty_line",
#             data={"whitespace": match.group("whitespace")},
#             chunk=chunk,
#             parser=self,
#         )


# class SkipChunk(ChunkParser):
#     """
#     A parser that will skip a chunk without advancing the state.
#     """

#     def __init__(self) -> None:
#         pass

#     def parse(
#         self,
#         chunk: Chunk,
#         state: str,
#         parse_hints: Dict | None = None,
#     ) -> ParseResult:
#         _ = parse_hints
#         return ParseResult(state, {}, self, chunk)
