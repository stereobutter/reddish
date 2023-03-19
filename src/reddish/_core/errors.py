class BrokenConnectionError(Exception):
    def __init__(self, msg="Connection closed.", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UnsupportedCommandError(Exception):
    pass


class CommandError(Exception):
    """Raised for Redis error replies.

    The original error code and message are available as
    attributes `.code` and `.message`.
    """

    def __init__(self, reply: str):
        self.code, self.message = str(reply).split(maxsplit=1)
