from hypothesis import given, settings
# functions under test
from reddish._parser import parse

from .strategies import complex_type, type_and_value


@settings(max_examples=1000)
@given(example=type_and_value(complex_type))
def test_parse_values_unchanged(example):
    type_, value = example
    assert value == parse(type_, value)
