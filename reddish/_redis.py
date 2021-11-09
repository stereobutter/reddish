from itertools import chain
from trio.abc import Stream
from hiredis import Reader

from ._command import Command
from ._utils import to_resp_array, partition
from ._errors import ConnectionClosedError


UNSUPPORTED_COMMANDS = (
    'SUBSCRIBE',
    'UNSUBSCRIBE'
    'PSUBSCRIBE',
    'PUNSUBSCRIBE',
    'MONITOR'
)


class UnsupportedCommandError(Exception): 
    pass


class Redis:

    def __init__(self, stream: Stream):
        """Redis client for executing commands over the supplied stream"""
        self._stream = stream
        self._reader = Reader()

    async def execute(self, command: Command, /, *commands: Command):

        commands = (command, *commands)
        await self._stream.send_all(b''.join(bytes(cmd) for cmd in commands))

        expected_num_replies = [len(cmd) for cmd in commands]
        replies = await self._read_reply(expected=sum(expected_num_replies))

        output = tuple(
            cmd._parse_response(*data)
            for cmd, data in zip(commands, partition(replies, expected_num_replies))
            )

        if len(output) == 1:
            return output[0]
        else:
            return output

    async def _read_reply(self, expected=1):
        """Read and parse replies from connection.
        ``expected`` is the amount of expected replies. In case of
        pipelining this number is set to the amount of commands sent.
        """
        replies = []

        while True:
            data = await self._stream.receive_some()
            if data == b'':
                raise ConnectionClosedError('connection unexpectedly closed')
            self._reader.feed(data)
            while True:
                reply = self._reader.gets()
                if reply is False:
                    break  # Read more data, go back to the outer loop.
                replies.append(reply)
                if len(replies) == expected:
                    return replies