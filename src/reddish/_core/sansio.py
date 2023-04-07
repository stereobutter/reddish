import hiredis
from outcome import capture, Error

from typing import Iterable, Any

from .utils import partition
from .errors import ConnectionError, PipelineError
from .supported_commands import check_for_unsupported_commands

from .typing import CommandType

NOT_ENOUGH_DATA = object()


class ReplyBuffer:
    def __init__(self, commands: Iterable[CommandType]):
        self._commands = commands
        self._expected_replies = [len(cmd) for cmd in commands]
        self._buffer: list[Any] = []

    def append(self, reply: Any) -> None:
        self._buffer.append(reply)

    @property
    def complete(self) -> bool:
        return len(self._buffer) == sum(self._expected_replies)

    def parse_replies(self) -> Any:
        replies = partition(self._buffer, self._expected_replies)

        outcomes = tuple(
            capture(cmd._parse_response, *reply)
            for cmd, reply in zip(self._commands, replies)
        )

        if any(isinstance(outcome, Error) for outcome in outcomes):
            raise PipelineError(outcomes)
        else:
            return [outcome.unwrap() for outcome in outcomes]


class ProtocolError(Exception):
    pass


class RedisSansIO:
    def __init__(self, reader=None):
        self._reader = reader or hiredis.Reader(notEnoughData=NOT_ENOUGH_DATA)
        self._reply_buffer = None
        self._broken = False

    def mark_broken(self):
        self._broken = True

    def send(self, commands: Iterable[CommandType]) -> bytes:
        if self._broken:
            raise ConnectionError()
        if self._reply_buffer is not None:
            raise ProtocolError("Cannot send more commands")
        for cmd in commands:
            check_for_unsupported_commands(cmd)
        self._reply_buffer = ReplyBuffer(commands)
        return b"".join(bytes(cmd) for cmd in commands)

    def receive(self, data: bytes) -> Any:
        reply_buffer = self._reply_buffer

        if self._broken:
            raise ConnectionError()
        if reply_buffer is None:
            raise ProtocolError(
                "Cannot receive replies because no commands where queued"
            )
        reader = self._reader
        reader.feed(data)

        while True:
            reply = reader.gets()
            if reply is NOT_ENOUGH_DATA:
                break  # no more complete replies in the reader
            else:
                reply_buffer.append(reply)

        if reply_buffer.complete:
            assert not reader.has_data(), "reader has more data but shouldnt"
            self._reply_buffer = None
            return reply_buffer.parse_replies()
        else:
            return NOT_ENOUGH_DATA
