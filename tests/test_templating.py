import pytest
from reddish._core.templating import (
    apply_template,
    format_original_field,
    parse_command_template,
)


def test_positional_args():

    assert (
        # (text, field, spec, conversion)
        [("", 0, "", None), ("", 1, "", None)]
        == list(parse_command_template("{}{}"))
        == list(parse_command_template("{0}{1}"))
    )


def test_keyword_args():
    # (text, field, spec, conversion)
    assert [("", "foo", "", None), ("", "bar", "", None)] == list(
        parse_command_template("{foo}{bar}")
    )


def test_apply_template_with_positional_args():
    assert (
        ["SET", "foo", "bar"]
        == apply_template("SET {} {}", "foo", "bar")
        == apply_template("SET {0} {1}", "foo", "bar")
    )


def test_apply_template_with_keyword_args():
    assert ["SET", "foo", "bar"] == apply_template(
        "SET {foo} {bar}", foo="foo", bar="bar"
    )


def test_format_original_field():
    assert "foo!s:f" == format_original_field("foo", "f", "s")


def test_apply_template_with_modifiers():
    with pytest.raises(ValueError):
        apply_template("{foo!s:f}")


def test_apply_template_with_missing_positional_args():
    with pytest.raises(TypeError):
        apply_template("{}{}", 1)


def test_apply_template_with_missing_keyword_args():
    with pytest.raises(TypeError):
        apply_template("{foo}{bar}", foo=1)
