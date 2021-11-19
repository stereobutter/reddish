from trio.abc import Stream
from hiredis import Reader

from ._command import Command, MultiExec
from ._utils import partition
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
        """Redis client for executing commands.

        Args:
            stream: a `trio.abc.Stream` connected to a redis server.
        """
        self._stream = stream
        self._reader = Reader()

    async def execute(self, command: Command):
        """Execute a single redis command.

        Args:
            command: The command to be executed.

        Returns:
            Response from redis as received or parsed into the type
            provided to the command.
        """
        [response] = await self.execute_many(command)
        return response

    async def execute_many(self, *commands: Command):
        """Execute multiple redis commands at once.

        Args:
            *commands: The commands to be executed.

        Returns:
            Responses from redis as received or parsed into the types
            provided to the commands.
        """
        def guard(command):
            if cmd._command_name.upper() in UNSUPPORTED_COMMANDS:
                raise UnsupportedCommandError(f"The '{cmd._command_name}' command is not supported.")

        for cmd in commands:
            if isinstance(tx := cmd, MultiExec):
                for cmd in tx:
                    guard(cmd)
            else:
                guard(cmd)

        await self._stream.send_all(b''.join(bytes(cmd) for cmd in commands))

        expected_num_replies = [len(cmd) for cmd in commands]
        replies = await self._read_reply(expected=sum(expected_num_replies))

        output = tuple(
            cmd._parse_response(*data)
            for cmd, data in zip(commands, partition(replies, expected_num_replies))
        )

        return output

    async def _read_reply(self, expected=1):
        # Read and parse replies from connection.
        # ``expected`` is the amount of expected replies. In case of
        # pipelining this number is set to the amount of commands sent.

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
