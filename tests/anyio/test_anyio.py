import anyio
import pytest
from reddish.backends.anyio import Redis
from reddish import Command
from reddish._core.errors import ConnectionError

pytestmark = pytest.mark.anyio


@pytest.fixture
async def connection():
    return anyio.connect_tcp("localhost", 6379)


@pytest.fixture
async def redis(connection):
    return Redis(await connection)


@pytest.fixture
def ping():
    return Command("PING").into(str)


async def test_execute(redis, ping):
    "PONG" == await redis.execute(ping)


async def test_execute_many(redis, ping):
    ["PONG", "PONG"] == await redis.execute_many(ping, ping)


async def test_stream(connection):
    with pytest.raises(TypeError):
        Redis(connection)


async def test_closed_connection(connection, ping):
    async with await connection as stream:
        redis = Redis(stream)

    with pytest.raises(ConnectionError):
        await redis.execute(ping)


async def test_concurrent_requests(redis, ping):
    async with anyio.create_task_group() as task_group:
        for i in range(10):
            task_group.start_soon(redis.execute, ping)


async def test_cancellation(redis, ping):
    # instructs redis server to close connection
    await redis.execute(Command("QUIT"))

    with pytest.raises(ConnectionError):
        await redis.execute(ping)
