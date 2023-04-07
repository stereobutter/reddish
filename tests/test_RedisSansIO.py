import pytest
from outcome import Error, Value
from reddish._core import Command, MultiExec
from reddish._core.sansio import RedisSansIO, ProtocolError, NOT_ENOUGH_DATA
from reddish._core.errors import UnsupportedCommandError, ConnectionError, PipelineError


@pytest.fixture
def redis():
    return RedisSansIO()


@pytest.fixture
def ping():
    return Command("PING").into(str)


def test_sending_command(redis, ping):
    assert bytes(ping) == redis.send([ping])


def test_sending_multiple_commands(redis, ping):
    assert 2 * bytes(ping) == redis.send([ping, ping])


def test_receiving(redis, ping):
    redis.send([ping])
    assert ["PONG"] == redis.receive(b"+PONG\r\n")


def test_receiving_in_chunks(redis, ping):
    redis.send([ping])
    assert redis.receive(b"+PONG") is NOT_ENOUGH_DATA
    assert ["PONG"] == redis.receive(b"\r\n")


def test_sending_repeatedly_should_raise(redis, ping):
    with pytest.raises(ProtocolError):
        redis.send([ping])
        redis.send([ping])


def test_receiving_without_send_should_raise(redis):
    with pytest.raises(ProtocolError):
        redis.receive(b"+PONG")


def test_broken_connection_send(redis):
    redis.mark_broken()
    with pytest.raises(ConnectionError):
        redis.send(ping)


def test_broken_connection_receive(redis):
    redis.mark_broken()
    with pytest.raises(ConnectionError):
        redis.receive(b"")


def test_unsupported_commands(redis):
    with pytest.raises(UnsupportedCommandError):
        redis.send([Command("SUBSCRIBE foo")])


def test_unsupported_commands_in_transaction(redis):
    with pytest.raises(UnsupportedCommandError):
        redis.send([MultiExec(Command("SUBSCRIBE foo"))])


def test_errors_in_pipeline(redis):
    with pytest.raises(PipelineError):
        try:
            redis.send([Command("PING"), Command("bar")])
            redis.receive(b"+PONG\r\n")
            redis.receive(b"-Error message\r\n")
        except PipelineError as error:
            assert len(error.outcomes) == 2
            first_reply, second_reply = error.outcomes
            assert isinstance(first_reply, Value) and isinstance(second_reply, Error)
            raise
