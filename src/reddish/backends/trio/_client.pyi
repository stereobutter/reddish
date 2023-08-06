import trio
from reddish.backends._client_stubs import AsyncRedis

class Redis(AsyncRedis):
    def __init__(self, stream: trio.abc.Stream) -> None: ...
