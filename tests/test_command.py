import pytest
from hypothesis import given
import hypothesis.strategies as st
import hiredis
from .strategies import type_and_value, complex_type

from reddish._command import Command, MultiExec

@given(example=type_and_value(complex_type))
def test_command_parses_data(example):
    type_, value = example
    assert value == Command('foo').into(type_)._parse_response(value)


def test_empty_Command():
    with pytest.raises(ValueError):
        Command('')

def test_command_serialization():
    reader = hiredis.Reader()
    reader.feed(bytes(Command('SET {foo} {bar}', foo='foo', bar='bar')))
    assert [b'SET', b'foo', b'bar'] == reader.gets()


@given(num=st.integers(min_value=0, max_value=1000))
def test_multi_exec_dump(num):
    reader = hiredis.Reader()
    tx = MultiExec(*(Command('foo') for _ in range(num)))
    reader.feed(bytes(tx))

    assert [b'MULTI'] == reader.gets()
    for _ in range(num):
        assert [b'foo'] == reader.gets()
    assert [b'EXEC'] == reader.gets()


@given(example=type_and_value(complex_type))
def test_multi_exec_parser(example):
    type_, value = example
    tx = MultiExec(Command('foo').into(type_))

    assert [value] == tx._parse_response(b'OK', b'QUEUED', [value])

@pytest.fixture
def tx():
    return MultiExec(Command('foo'), Command('bar'))

def test_multi_exec_error(tx):
    cause_error = Exception('cause')
    exec_error = Exception('exec aborted')
    [exec_error, cause_error] = tx._parse_response(b'OK', b'QUEUED', cause_error, exec_error)

def test_multi_exec_wrong_num_of_responses(tx):
    with pytest.raises(AssertionError):
        tx._parse_response(b'OK', b'QUEUED', b'QUEUED', ['foo'])

def test_multi_exec_multi_non_ok_response(tx):
    with pytest.raises(ValueError):
        tx._parse_response(Exception('...'), b'QUEUED', b'QUEUED', ['foo', 'bar'])