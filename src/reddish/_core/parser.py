from pydantic import parse_obj_as, ValidationError
from reddish._core.errors import ParseError


def parse(type_, value):
    try:
        return parse_obj_as(type_, value)
    except ValidationError as error:
        raise ParseError(value, type_) from error
