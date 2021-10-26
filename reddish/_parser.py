from pydantic import parse_obj_as, ValidationError


class ParseError(Exception):
    pass


def parse(type_, value):
    try:
        return parse_obj_as(type_, value)
    except ValidationError as error:
        raise ParseError(f'`{repr(value)}` could not be parsed as `{type_}`') from error
