class BrokenConnectionError(Exception):
    def __init__(self, msg='Connection closed.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UnsupportedCommandError(Exception):
    pass
