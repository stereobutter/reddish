import socket
import threading
from reddish._core.sansio import RedisSansIO, NOT_ENOUGH_DATA
from reddish._core.errors import ConnectionError


class Redis:
    def __init__(self, stream: socket.socket):
        """Redis client for executing commands.

        Args:
            stream: a `socket.socket` connected to a redis server.
        """

        if not isinstance(stream, socket.socket):
            TypeError(f"'{repr(stream)}' is not an instance of '{repr(socket.socket)}'")
        try:
            stream.getpeername()
        except OSError:
            raise TypeError(f"'{repr(stream)}' is not connected") from None
        self._stream = stream
        self._lock = threading.Lock()
        self._redis = RedisSansIO()

    def execute_many(self, *commands):
        """Execute multiple redis commands at once.

        Args:
            *commands: The commands to be executed.

        Returns:
            Responses from redis as received or parsed into the types
            provided to the commands.
        """

        redis = self._redis
        stream = self._stream

        with self._lock:
            try:
                request = redis.send(commands)
                stream.sendall(request)

                while True:
                    data = stream.recv(4096)
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

    def execute(self, command):
        """Execute a single redis command.

        Args:
            command: The command to be executed.

        Returns:
            Response from redis as received or parsed into the type
            provided to the command.
        """
        return self.execute_many(command)[0]
