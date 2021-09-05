import pytest
from hypothesis import given
import hypothesis.strategies as st
from .strategies import type_and_value, complex_type

from reddish._command import Command

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