try:
    import anyio
except ImportError:
    raise ImportError("Execute 'pip install reddish[anyio]' to enable anyio support")
from reddish._core.sansio import RedisSansIO, NOT_ENOUGH_DATA
from reddish._core.errors import ConnectionError


class Redis:
    def __init__(self, stream: anyio.abc.ByteStream) -> None:  # type: ignore
        """Redis client for executing commands.

        Args:
            stream: a `anyio.abc.ByteStream` connected to a redis server.
        """

        if not isinstance(stream, anyio.abc.ByteStream):  # type: ignore
            raise TypeError(
                f"'{repr(stream)}' is not an instance of 'anyio.abc.ByteStream'"
            )
        self._stream = stream
        self._lock = anyio.Lock()
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
        stream = self._stream

        async with self._lock:
            try:
                request = redis.send(commands)
                await stream.send(request)

                while True:
                    data = await stream.receive(4096)
                    replies = redis.receive(data)
                    if replies is NOT_ENOUGH_DATA:
                        continue
                    else:
                        return replies
            except (
                anyio.EndOfStream,
                anyio.ClosedResourceError,
                anyio.BrokenResourceError,
            ):
                redis.mark_broken()
                raise ConnectionError()
            except BaseException:
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
