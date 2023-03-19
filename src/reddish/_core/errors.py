class ConnectionError(Exception):
    """Raised when the underlying connection closed or failed."""

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


class ParseError(Exception):
    """Raised for commands where reply does not parse successfully.

    The original reply and the type that it failed to be parsed into as attributed
    `.reply` and `.type`
    """

    def __init__(self, reply, type):
        self._reply = reply
        self._type = type

    @property
    def reply(self):
        return self._reply

    @property
    def type(self):
        return self._type


class PipelineError(Exception):
    """Raised when one or more pipelined commands resulted in an error.

    The values and/or errors are made available as `Outcome` objects and can be
    iterated over by iterating this exception.
    """

    def __init__(self, outcomes):
        self._outcomes = outcomes

    @property
    def outcomes(self):
        return self._outcomes


class TransactionError(Exception):
    """Raised when one or more commands in a Multi/Exec transaction
    resulted in an error.

    The values and/or errors are made available as `Outcome` objects and can be
    iterated over by iterating this exception.
    """

    def __init__(self, outcomes):
        self._outcomes = outcomes

    @property
    def outcomes(self):
        return self._outcomes
