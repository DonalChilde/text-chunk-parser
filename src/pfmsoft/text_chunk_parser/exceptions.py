# # -*- coding: utf-8 -*-
# #
# #  exceptions.py
# #  _project_
# #
# #  Created by Chad Lowe on 2022-05-19.
# #  Copyright 2022 Chad Lowe. All rights reserved.
# #
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
