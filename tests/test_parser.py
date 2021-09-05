import hypothesis.strategies as st
from hypothesis import given, settings, Verbosity
import json
from typing import Union

#functions under test
from reddish._parser import parse

primitive_type = st.sampled_from([int, bool, str, type(None)])


@st.composite
def generic_list_type(draw, item_type_strategy):
    item_type = draw(item_type_strategy)
    return list[item_type]

@st.composite
def generic_dict_type(draw, key_type_strategy, value_type_stategy):
    key_type = draw(key_type_strategy)
    value_type = draw(value_type_stategy)
    return dict[key_type, value_type]

@st.composite
def union_type(draw, type_strategy):
    num = draw(st.integers(min_value=2, max_value=5))
    return Union[tuple(draw(type_strategy) for _ in range(num))]


complex_type =  st.recursive(
    primitive_type, 
    lambda children: generic_list_type(children) | generic_dict_type(st.just(str), children),  #| union_type(children), 
    max_leaves=4
)

@st.composite
def type_and_value(draw, type_strategy):
    type_ =  draw(type_strategy)
    value = draw(st.from_type(type_))
    return type_, value


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