import pytest
from reddish._command import Command, MultiExec
from reddish._sansio import RedisSansIO, ProtocolError
from reddish._errors import UnsupportedCommandError


@pytest.fixture
def redis():
    return RedisSansIO()


def test_sending_command(redis):
    cmd = Command('PING')
    assert bytes(cmd) == redis.send([Command('PING')])


def test_sending_multiple_commands(redis):
    cmd = Command('PING')
    assert 2 * bytes(cmd) == redis.send([Command('PING'), Command('PING')])


def test_receiving(redis):
    redis.send([Command('PING').into(str)])
    assert ['PONG'] == redis.receive(b'+PONG\r\n')


def test_receiving_in_chunks(redis):
    redis.send([Command('PING').into(str)])
    assert [] == redis.receive(b'+PONG')
    assert ['PONG'] == redis.receive(b'\r\n')


def test_sending_repeatedly_should_raise(redis):
    with pytest.raises(ProtocolError):
        redis.send([Command('PING')])
        redis.send([Command('PING')])


def test_receiving_without_send_should_raise(redis):
    with pytest.raises(ProtocolError):
        redis.receive(b'+PONG')


def test_unsupported_commands(redis):
    with pytest.raises(UnsupportedCommandError):
        redis.send([Command('SUBSCRIBE foo')])


def test_unsupported_commands_in_transaction(redis):
    with pytest.raises(UnsupportedCommandError):
        redis.send([MultiExec(Command('SUBSCRIBE foo'))])
