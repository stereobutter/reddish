import pytest
from reddish import Redis, Command, MultiExec
async def test_unsupported_commands():
    with pytest.raises(Exception):
        redis = Redis(None)  # doesn't need a stream to reach the command check
        await redis.execute(Command('SUBSCRIBE foo'))


async def test_unsupported_commands_in_transaction():
    with pytest.raises(Exception):
        redis = Redis(None)
        await redis.execute(MultiExec(Command('SUBSCRIBE foo')))

