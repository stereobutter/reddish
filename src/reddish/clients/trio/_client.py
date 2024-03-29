try:
    import trio
except ImportError:
    raise ImportError("Execute 'pip install reddish[trio]' to enable trio support")
from reddish._core.sansio import RedisSansIO, NOT_ENOUGH_DATA
from reddish._core.errors import ConnectionError


class Redis:
    def __init__(self, stream: trio.abc.Stream) -> None:
        """Redis client for executing commands.

        Args:
            stream: a `trio.abc.Stream` connected to a redis server.
        """

        if not isinstance(stream, trio.abc.Stream):
            raise TypeError(f"'{repr(stream)}' is not an instance of 'trio.abc.Stream'")
        self._stream = stream
        self._lock = trio.Lock()
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
                await stream.send_all(request)

                while True:
                    data = await stream.receive_some()
                    if data == b"":
                        raise ConnectionError()
                    replies = redis.receive(data)
                    if replies is NOT_ENOUGH_DATA:
                        continue
                    else:
                        return replies
            except (trio.BrokenResourceError, trio.ClosedResourceError):
                redis.mark_broken()
                raise ConnectionError()
            except trio.Cancelled:
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
