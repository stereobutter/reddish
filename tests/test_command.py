import pytest
from hypothesis import given
import hypothesis.strategies as st
from .strategies import type_and_value, complex_type

from reddish._command import Command, MultiExec

@given(example=type_and_value(complex_type))
def test_command_parses_data(example):
    type_, value = example
    assert value == Command().into(type_)._parse_response(value)

@given(example=complex_type.flatmap(st.from_type))
def test_command_dump_parts(example):
    cmd = Command(example)
    dump = cmd._dump_parts()
    assert len(dump) == 1, "dumped to the wrong number of parts"
    assert isinstance(dump[0], bytes), "dumped to the wrong type"


def test_command_subclass():

    class Get(Command):

        def _make(self, key):
            return ('GET', key)

    assert Get('foo')._dump_parts() == Command('GET', 'foo')._dump_parts()

    with pytest.raises(TypeError):
        Get('foo', 'bar')  # invalid Command construction


@given(num=st.integers(min_value=0, max_value=1000))
def test_multi_exec_dump(num):
    tx = MultiExec(*(Command('foo') for _ in range(num)))
    assert len(tx._dump()) == num + 2


@given(example=type_and_value(complex_type))
def test_multi_exec_parser(example):
    type_, value = example
    tx = MultiExec(Command().into(type_))

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