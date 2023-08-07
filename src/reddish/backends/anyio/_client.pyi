import anyio
from reddish.backends._client_stubs import AsyncRedis

class Redis(AsyncRedis):
    def __init__(self, stream: anyio.abc.ByteStream) -> None: ...  # type: ignore
