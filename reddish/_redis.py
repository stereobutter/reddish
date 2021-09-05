from itertools import chain
from trio.abc import Stream
from hiredis import Reader

from ._command import Command
from ._utils import to_resp_array, partition
from ._errors import ConnectionClosedError

class Redis:

    def __init__(self,stream: Stream):
        """Redis client for executing commands over the supplied stream"""
        self._stream = stream
        self._reader = Reader()

    async def execute(self, command: Command, /, *commands: Command):

        commands = (command, *commands)

        # build the command(s)
        dumps = [cmd._dump() for cmd in commands]
        raw_commands = list(chain.from_iterable(dumps))
        request = b''.join([to_resp_array(*cmd) for cmd in raw_commands])
        await self._stream.send_all(request)
        replies = await self._read_reply(expected=len(raw_commands))

        chunks_sizes = [len(dump) for dump in dumps]

        output = tuple(
            cmd._parse_response(*data)
            for cmd, data in zip(commands, partition(replies, chunks_sizes))
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