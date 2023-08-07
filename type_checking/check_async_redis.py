from reddish import Command, MultiExec
from reddish.clients._client_stubs import AsyncRedis as Redis
from typing import assert_type


async def check_execute(redis: Redis):
    result = await redis.execute(Command("...").into(int))
    assert_type(result, int)


async def check_execute_typeform(redis: Redis):
    result = await redis.execute(Command("...").into(int | str))
    assert_type(result, int | str)


async def check_execute_multiexec(redis: Redis):
    result = await redis.execute(
        MultiExec(
            Command("...").into(int),
            Command("...").into(str),
        )
    )
    assert_type(result, tuple[int, str])


async def check_execute_many_5(redis: Redis):
    result = await redis.execute_many(
        Command("...").into(int),
        Command("...").into(str),
        Command("...").into(bool),
        Command("...").into(float),
        Command("...").into(None),
    )
    assert_type(result, tuple[int, str, bool, float, None])


async def check_execute_many_3_with_transaction(redis: Redis):
    result = await redis.execute_many(
        Command("...").into(int),
        MultiExec(
            Command("...").into(str),
            Command("...").into(bool),
            Command("...").into(float),
        ),
        Command("...").into(None),
    )
    assert_type(result, tuple[int, tuple[str, bool, float], None])


async def check_execute_many_more_than_5(redis: Redis):
    result = await redis.execute_many(
        Command("...").into(bool),
        Command("...").into(str),
        Command("...").into(int),
        Command("...").into(float),
        Command("...").into(None),
        Command("...").into(str),
    )
    assert_type(result, tuple[int | str | float | bool | None, ...])
