from pydantic import parse_obj_as, ValidationError
from reddish._core.errors import ParseError
from typing import Type, Any, TypeVar

T = TypeVar("T")


def parse(type_: Type[T], value: Any) -> T:
    try:
        return parse_obj_as(type_, value)
    except ValidationError as error:
        raise ParseError(value, type_) from error
