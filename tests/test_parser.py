import hypothesis.strategies as st
from hypothesis import given, settings
import json

from .strategies import type_and_value, complex_type, generic_dict_type, generic_list_type

#functions under test
from reddish._parser import parse


@settings(max_examples=1000)
@given(example=type_and_value(complex_type))
def test_parse_values_unchanged(example):
    type_, value = example
    assert value == parse(type_, value)

@settings(max_examples=1000)
@given(example=type_and_value(complex_type))
def test_parse_values_from_json(example):
    type_, value = example
    assert value == parse(type_, json.dumps(value))

@settings(max_examples=1000)
@given(example=type_and_value(generic_list_type(complex_type)))
def test_parse_values_from_list(example):
    type_, value = example
    assert value == parse(type_, [json.dumps(x) for x in value])

@settings(max_examples=1000)
@given(example=type_and_value(generic_dict_type(st.just(str), complex_type)))
def test_parse_values_from_dict(example):
    type_, value = example
    assert value == parse(type_, {json.dumps(k):json.dumps(v) for k, v in value.items()})