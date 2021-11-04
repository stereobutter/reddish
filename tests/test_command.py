import pytest
from hypothesis import given
import hypothesis.strategies as st
from .strategies import type_and_value, complex_type

from reddish._command import Command, MultiExec

@given(example=type_and_value(complex_type))
def test_command_parses_data(example):
    type_, value = example
    assert value == Command('').into(type_)._parse_response(value)



@given(num=st.integers(min_value=0, max_value=1000))
def test_multi_exec_dump(num):
    tx = MultiExec(*(Command('foo') for _ in range(num)))
    assert len(tx._dump()) == num + 2


@given(example=type_and_value(complex_type))
def test_multi_exec_parser(example):
    type_, value = example
    tx = MultiExec(Command('').into(type_))

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