import trio
import pytest_trio
import pytest
from reddish.trio import Redis, Command
from reddish._errors import BrokenConnectionError


@pytest_trio.trio_fixture
async def connection():
    return trio.open_tcp_stream('localhost', 6379)


@pytest_trio.trio_fixture
async def redis(connection):
    return Redis(await connection)


@pytest.fixture
def ping():
    return Command('PING').into(str)


async def test_execute(redis, ping):
    'PONG' == await redis.execute(ping)


async def test_execute_many(redis, ping):
    ['PONG', 'PONG'] == await redis.execute_many(ping, ping)


async def test_stream(connection):
    with pytest.raises(TypeError):
        Redis(connection)


async def test_closed_connection(connection, ping):
    async with await connection as stream:
        redis = Redis(stream)

    with pytest.raises(BrokenConnectionError):
        await redis.execute(ping)


async def test_concurrent_requests(redis, ping):
    async with trio.open_nursery() as nursery:
        for i in range(10):
            nursery.start_soon(redis.execute, ping)
