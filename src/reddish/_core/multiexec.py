from __future__ import annotations

from outcome import capture, Error
from hiredis import ReplyError, pack_command

from .errors import CommandError, TransactionError

from typing import TypeVar, Generic


T = TypeVar("T")

OK = b"OK"
QUEUED = b"QUEUED"


class MultiExec(
    Generic[T]
):  # must inherit from Generic[T] to be subscribable at runtime
    """A redis MULTI and EXEC transaction"""

    _MULTI = pack_command((b"MULTI",))
    _EXEC = pack_command((b"EXEC",))

    def __init__(self, *commands):
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

        if isinstance(replies, ReplyError):
            error = CommandError(str(replies))
            for resp in acks:
                if not resp == QUEUED:
                    break
            failed_ack = next(resp for resp in acks if resp != QUEUED)
            cause = CommandError(str(failed_ack))
            raise error from cause

        assert len(replies) == len(
            self._commands
        ), "Got wrong number of replies from transaction"

        outcomes = tuple(
            capture(cmd._parse_response, reply)
            for cmd, reply in zip(self._commands, replies)
        )

        if any(isinstance(outcome, Error) for outcome in outcomes):
            raise TransactionError(outcomes)
        else:
            return [outcome.unwrap() for outcome in outcomes]

    def __bytes__(self):
        commands = b"".join(bytes(cmd) for cmd in self._commands)
        return b"%b%b%b" % (self._MULTI, commands, self._EXEC)

    def __repr__(self):
        commands = (repr(cmd) for cmd in self._commands)
        return f"{self.__class__.__name__}({', '.join(commands)})"

    def __iter__(self):
        yield from self._commands

    def __len__(self):
        return 2 + len(self._commands)  # MULTI cmds... EXEC
