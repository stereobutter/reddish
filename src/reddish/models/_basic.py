from dataclasses import dataclass

from hiredis import ReplyError


class Ok:

    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @classmethod
    def _validate(cls, value):

        if isinstance(value, cls):
            return value
        elif b'OK' == value:
            return cls
        else:
            raise ValueError('value is not a valid redis OK response')


@dataclass(frozen=True)
class ErrorMessage:

    code: str
    message: str

    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @classmethod
    def _validate(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, ReplyError):
            code, message = str(value).split(maxsplit=1)
            return cls(code, message)
        else:
            raise TypeError('value is not a valid redis error reply')
