from collections import deque
from typing import Any, Deque, Optional, Sequence


class ChunkParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedParseException(ChunkParserException):
    def __init__(
        self,
        msg: Optional[str],
        chunk: "Chunk",
        parser: "Parser",
        context: "ParseContext",
        *args: object,
    ) -> None:
        if msg is None:
            msg = "Failed to parse. No details available."
        message = f"explaination: {msg}\nchunk: {chunk!r}\nparser: {parser!r}\ncontext: {context!r}"
        super().__init__(message)
        self.msg = msg
        self.chunk = chunk
        self.parser = parser
        self.context = context


class Chunk:
    def __init__(self, key, text: str) -> None:
        # can make this an object with page number, line number
        self.key = key
        self.text = text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key: {self.key!r}, text: {self.text})"


class ParseContext:
    def __init__(self, obj: Any, results_size: int = 3) -> None:
        # A user defined object used for intermediate results
        self.obj = obj
        # a list/queue/something of previous ParseResults
        self.parse_results: Deque[ParseResult] = deque(maxlen=results_size)
        self.parse_state: str = "Origin"
        # a list/queue/something of future Chunks
        self.future_chunks = None


class ParseResult:
    def __init__(self, chunk: Chunk, parser: "Parser", data: Any) -> None:
        self.chunk = chunk
        self.parser = parser
        self.data = data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(chunk: {self.chunk!r}, parser: {self.parser!r}, data: {self.data!r})"


class Parser:
    def parse_chunk(self, context: ParseContext, chunk: Chunk) -> ParseResult:
        pass

    def parse_callback(self, context: ParseContext, parse_result: ParseResult):
        pass

    def state_key(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>()"


class ParseInstruction:
    def __init__(
        self,
        parser: Parser,
        advance_state_on_match: bool = True,
    ) -> None:
        self.parser = parser
        self.advance_state_on_match = advance_state_on_match


class ParseSchema:
    # a lookup table for parse scheme, showing next expected parsers
    def parse_instructions(self, parse_state: str) -> Sequence[ParseInstruction]:
        pass


class ParseListener:
    def report_match(
        self, chunk: Chunk, instruction: ParseInstruction, context: ParseContext
    ):
        pass

    def report_not_match(
        self,
        explaination: str,
        chunk: Chunk,
        instruction: ParseInstruction,
        context: ParseContext,
    ):
        pass

    def report_no_matches(
        self,
        chunk: Chunk,
        instructions: Sequence[ParseInstruction],
        context: ParseContext,
    ):
        pass


class ChunkParser:
    # place where the work happens.
    # get parse scheme
    # loop over chunks from chunk provider
    # parse chunk
    # check for successful parse,do parse callbacks on successful parse
    # report to listeners
    # continue till complete

    def __init__(
        self, parse_schema: ParseSchema, listeners: Sequence[ParseListener]
    ) -> None:
        self.parse_schema = parse_schema
        self.listeners = listeners

    def parse_chunks(self, chunks, context: ParseContext):
        for chunk in chunks:
            parse_state = context.parse_state
            instructions = self.parse_schema.parse_instructions(parse_state=parse_state)
            for instruction in instructions:
                try:
                    result = instruction.parser.parse_chunk(context, chunk)
                    instruction.parser.parse_callback(context, result)
                    context.parse_results.append(result)
                    if instruction.advance_state_on_match:
                        context.parse_state = instruction.parser.state_key()
                    for listener in self.listeners:
                        listener.report_match(chunk, instruction, context)
                    return
                except FailedParseException as ex:

                    for listener in self.listeners:
                        listener.report_not_match(ex.msg, chunk, instruction, context)
            for listener in self.listeners:
                listener.report_no_matches(chunk, instructions, context)
