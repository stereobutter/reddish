from __future__ import annotations
from collections.abc import Iterable

from typing import Union

from reddish._utils import to_resp_array
from reddish.core.command import Command

AtomicType = Union[int, float, str, bytes]


OK = b"OK"
QUEUED = b"QUEUED"


class MultiExec:
    """A redis MULTI and EXEC transaction"""

    _MULTI = to_resp_array(b"MULTI")
    _EXEC = to_resp_array(b"EXEC")

    def __init__(self, *commands: Command) -> None:
        """Create transaction from commands.

        Args:
            *commands: Commands to include in the transaction
        """
        self._commands = commands

    def _parse_response(self, *responses):
        assert (
            len(responses) == len(self._commands) + 2
        ), "Got wrong number of replies from pipeline"

        multi, *acks, replies = responses

        if not multi == OK:
            raise ValueError("Got '{multi}' from MULTI instead of '{OK}' ")

        if isinstance(replies, Exception):
            transaction_error = replies
            causes = [(i, resp) for i, resp in enumerate(acks) if not resp == QUEUED]
            output = [transaction_error for _ in self._commands]
            for i, cause in causes:
                output[i] = cause
            return output

        assert len(replies) == len(
            self._commands
        ), "Got wrong number of replies from transaction"
        return [
            cmd._parse_response(reply) for cmd, reply in zip(self._commands, replies)
        ]

    def __bytes__(self):
        commands = b"".join(bytes(cmd) for cmd in self._commands)
        return b"%b%b%b" % (self._MULTI, commands, self._EXEC)

    def __repr__(self) -> str:
        commands = (repr(cmd) for cmd in self._commands)
        return f"{self.__class__.__name__}({', '.join(commands)})"

    def __iter__(self) -> Iterable[Command]:
        yield from self._commands

    def __len__(self):
        return 2 + len(self._commands)  # MULTI cmds... EXEC
