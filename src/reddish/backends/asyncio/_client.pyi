import asyncio
from reddish.backends._client_stubs import AsyncRedis

class Redis(AsyncRedis):
    def __init__(
        self, streams: tuple[asyncio.StreamReader, asyncio.StreamWriter]
    ) -> None: ...
