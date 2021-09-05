import pytest
from hypothesis import given
from .strategies import type_and_value, complex_type

from reddish._command import Command

@given(example=type_and_value(complex_type))
def test_command_parses_data(example):
    type_, value = example
    assert value == Command().into(type_)._parse_response(value)

def test_command_subclass():

    class Get(Command):

        def _make(self, key):
            return ('GET', key)

    assert Get('foo')._dump_parts() == Command('GET', 'foo')._dump_parts()

    with pytest.raises(TypeError):
        Get('foo', 'bar')  # invalid Command construction