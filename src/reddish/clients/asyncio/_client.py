from __future__ import annotations
import asyncio
from reddish._core.sansio import RedisSansIO, NOT_ENOUGH_DATA
from reddish._core.errors import ConnectionError


class Redis:
    def __init__(
        self, streams: tuple[asyncio.StreamReader, asyncio.StreamWriter]
    ) -> None:
        """Redis client for executing commands.

        Args:
            streams: a `(StreamReader, StreamWriter)` pair connected to a redis server.
        """
        reader, writer = streams
        if not isinstance(reader, asyncio.StreamReader) and isinstance(
            writer, asyncio.StreamWriter
        ):
            raise TypeError(
                f"'{repr(streams)}' is not an pair of `(StreamReader, StreamWriter)`."
            )
        self._reader, self._writer = (reader, writer)
        self._lock = asyncio.Lock()
        self._redis = RedisSansIO()

    async def execute_many(self, *commands):
        """Execute multiple redis commands at once.

        Args:
            *commands: The commands to be executed.

        Returns:
            Responses from redis as received or parsed into the types
            provided to the commands.
        """

        redis = self._redis
        reader, writer = self._reader, self._writer

        async with self._lock:
            try:
                request = redis.send(commands)
                writer.write(request)
                await writer.drain()

                while True:
                    data = await reader.read(4096)
                    if data == b"":
                        raise ConnectionError()
                    replies = redis.receive(data)
                    if replies is NOT_ENOUGH_DATA:
                        continue
                    else:
                        return replies
            except OSError:
                redis.mark_broken()
                raise ConnectionError()
            except asyncio.CancelledError:
                redis.mark_broken()
                raise

    async def execute(self, command):
        """Execute a single redis command.

        Args:
            command: The command to be executed.

        Returns:
            Response from redis as received or parsed into the type
            provided to the command.
        """

        return (await self.execute_many(command))[0]
