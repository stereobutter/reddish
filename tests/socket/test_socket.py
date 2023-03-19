import socket
import pytest
from concurrent.futures import ThreadPoolExecutor

from reddish.socket import Redis, Command
from reddish._core.errors import BrokenConnectionError


@pytest.fixture
def unconnected_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@pytest.fixture
def connected_socket(unconnected_socket):
    unconnected_socket.connect(("localhost", 6379))
    yield unconnected_socket
    unconnected_socket.close()


@pytest.fixture
def redis(connected_socket):
    return Redis(connected_socket)


@pytest.fixture
def ping():
    return Command("PING").into(str)


def test_execute(redis, ping):
    "PONG" == redis.execute(ping)


def test_execute_many(redis, ping):
    ["PONG", "PONG"] == redis.execute_many(ping, ping)


def test_stream(unconnected_socket):
    with pytest.raises(TypeError):
        Redis(unconnected_socket)


def test_closed_connection(connected_socket, ping):
    redis = Redis(connected_socket)
    connected_socket.close()
    with pytest.raises(BrokenConnectionError):
        redis.execute(ping)


def test_concurrent_requests(redis, ping):
    with ThreadPoolExecutor(max_workers=10) as pool:
        for i in range(10):
            pool.submit(redis.execute, ping)
