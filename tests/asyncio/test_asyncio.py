import asyncio
import pytest
import pytest_asyncio
from reddish.backends.asyncio import Redis
from reddish import Command
from reddish._core.errors import ConnectionError

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def connection():
    return asyncio.open_connection("localhost", 6379)


@pytest_asyncio.fixture
async def redis(connection):
    return Redis(await connection)


@pytest.fixture
def ping():
    return Command("PING").into(str)


@pytest.mark.asyncio
async def test_execute(redis, ping):
    "PONG" == await redis.execute(ping)


@pytest.mark.asyncio
async def test_execute_many(redis, ping):
    ["PONG", "PONG"] == await redis.execute_many(ping, ping)


@pytest.mark.asyncio
async def test_stream(connection):
    with pytest.raises(TypeError):
        Redis(connection)


@pytest.mark.asyncio
async def test_closed_connection(connection, ping):
    reader, writer = await connection
    writer.close()
    redis = Redis((reader, writer))

    with pytest.raises(ConnectionError):
        await redis.execute(ping)


@pytest.mark.asyncio
async def test_concurrent_requests(redis, ping):
    await asyncio.gather(*[redis.execute(ping) for _ in range(10)])


@pytest.mark.asyncio
async def test_cancellation(redis, ping):
    # instructs redis server to close connection
    await redis.execute(Command("QUIT"))

    with pytest.raises(ConnectionError):
        await redis.execute(ping)
