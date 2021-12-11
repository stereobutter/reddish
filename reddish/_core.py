from ._utils import partition


class ReplyBuffer:

    def __init__(self, commands):
        self._commands = commands
        self._expected_replies = [len(cmd) for cmd in commands]
        self._buffer = []

    def append(self, reply):
        self._buffer.append(reply)

    @property
    def complete(self):
        return len(self._buffer) == self._expected_replies

    def parse_replies(self):
        replies = partition(self._buffer, self._expected_replies)
        return [cmd._parse_response(*reply) for cmd, reply in zip(self._commands, replies)]


class Redis:

    def send(self, commands):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
