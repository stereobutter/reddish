import hiredis
import hypothesis.strategies as st
import pytest
from hypothesis import given
from outcome import Value, Error
from hiredis import ReplyError

# functions under test
from reddish._core import Args, Command, MultiExec
from reddish._core.errors import CommandError, TransactionError, ParseError

from .strategies import complex_type, type_and_value


def test_repr():
    example = MultiExec(
        Command("PING"),
        Command("XADD {key} * {fields}", key="foo", fields=Args(["bar", "baz"])),
    )

    eval(repr(example))


@given(example=type_and_value(complex_type))
def test_command_parses_data(example):
    type_, value = example
    assert value == Command("foo").into(type_)._parse_response(value)


def test_command_parsing_fails():
    with pytest.raises(ParseError):
        try:
            Command("foo").into(int)._parse_response("hello")
        except ParseError as error:
            assert error.reply == "hello"
            assert error.type is int
            raise


def test_empty_Command():
    with pytest.raises(ValueError):
        Command("")


def test_command_serialization():
    reader = hiredis.Reader()
    reader.feed(bytes(Command("SET {foo} {bar}", foo="foo", bar="bar")))
    assert [b"SET", b"foo", b"bar"] == reader.gets()


def test_command_error():
    with pytest.raises(CommandError):
        try:
            Command("foo")._parse_response(ReplyError("ERRORCODE some error message"))
        except CommandError as error:
            assert error.code == "ERRORCODE"
            assert error.message == "some error message"
            raise


@given(num=st.integers(min_value=0, max_value=1000))
def test_multi_exec_dump(num):
    reader = hiredis.Reader()
    tx = MultiExec(*(Command("FOO") for _ in range(num)))
    reader.feed(bytes(tx))

    assert [b"MULTI"] == reader.gets()
    for _ in range(num):
        assert [b"FOO"] == reader.gets()
    assert [b"EXEC"] == reader.gets()


@given(example=type_and_value(complex_type))
def test_multi_exec_parser(example):
    type_, value = example
    tx = MultiExec(Command("foo").into(type_))

    assert [value] == tx._parse_response(b"OK", b"QUEUED", [value])


@pytest.fixture
def tx():
    return MultiExec(Command("foo"), Command("bar"))


def test_multi_exec_EXECABORT(tx):
    cause_error = ReplyError("SOME_ERROR some message")
    exec_error = ReplyError(
        "EXECABORT Transaction discarded because of previous errors."
    )
    with pytest.raises(CommandError):
        try:
            tx._parse_response(b"OK", b"QUEUED", cause_error, exec_error)
        except CommandError as error:
            cause = error.__cause__
            assert isinstance(error.__cause__, CommandError)
            assert cause.code == "SOME_ERROR"
            raise


def test_multi_exec_errors_in_transaction(tx):
    with pytest.raises(TransactionError):
        try:
            tx._parse_response(
                b"OK",
                b"QUEUED",
                b"QUEUED",
                [b"PONG", ReplyError("ERRORCODE some error message")],
            )
        except TransactionError as error:
            assert len(error.outcomes) == 2
            first_reply, second_reply = error.outcomes
            assert isinstance(first_reply, Value) and isinstance(second_reply, Error)
            raise


def test_multi_response_parsing(tx):
    assert [b"foo", b"bar"] == tx._parse_response(
        b"OK", b"QUEUED", b"QUEUED", [b"foo", b"bar"]
    )


def test_multi_exec_wrong_num_of_responses(tx):
    with pytest.raises(AssertionError):
        tx._parse_response(b"OK", b"QUEUED", b"QUEUED", ["foo"])


def test_multi_exec_multi_non_ok_response(tx):
    with pytest.raises(ValueError):
        tx._parse_response(Exception("..."), b"QUEUED", b"QUEUED", ["foo", "bar"])
