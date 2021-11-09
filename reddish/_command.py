from collections.abc import Mapping
from itertools import chain
from copy import copy
from ._parser import parse, ParseError
from ._utils import to_bytes, json_dumps
from ._templating import apply_template


class Args:

    def __init__(self, iterable):
        self._parts = []
        for part in iterable:
            if not isinstance(part, (int, float, str, bytes)):
                raise ValueError(f"''{repr(part)} is not a valid argument")
            self._parts.append(part)

    def __iter__(self):
        for part in self._parts:
            yield to_bytes(part)


    @classmethod
    def from_dict(cls, /, mapping):
        if not isinstance(mapping, Mapping):
            raise ValueError('Value is not a Mapping')
        return cls(chain.from_iterable(mapping.items()))


class Command:
    """Class for specifing a single redis command"""

    def __init__(self, template, *args, **kwargs):
        """Accepts strings and data to form a redis command"""
        self._parts = apply_template(template, *args, **kwargs)

        for part in self._parts:
            if not isinstance(part, (int, float, str, bytes, Args)):
                raise ValueError(f"''{repr(part)} is not valid as part of a command")

        self._models = ()

    def __repr__(self):
        parts = ((part if isinstance(part, (str, bytes)) else f'`{part}`' for part in self._parts))
        return f"""Command("{' '.join(parts)}")"""

    def into(self, model, /):
        """Parse the reponse into the provided type"""
        new = copy(self)
        new._models = (*self._models, model)
        return new

    def _parse_response(self, response):
        if not self._models:  # skip parsing
            return response

        for model in self._models:
            try:
                response = parse(model, response)
            except ParseError as error:
                return error

        return response

    def _dump_parts(self):
        for part in self._parts:
            if isinstance(part, Args):
                for sub_part in part._parts:
                    yield to_bytes(sub_part)
            else:
                yield to_bytes(part)

    def _dump(self):
        return [self._dump_parts()]


OK = b'OK'
QUEUED = b'QUEUED'


class MultiExec:
    """Class for wrapping commands into a redis MULTI and EXEC transaction"""

    def __init__(self, *commands: Command):
        self._commands = commands

    def _dump(self):
        return [[b'MULTI'], *[cmd._dump_parts() for cmd in self._commands], [b'EXEC']]

    def _parse_response(self, *responses):
        assert len(responses) == len(self._commands) + 2; "Got wrong number of replies from pipeline"

        multi, *acks, replies = responses

        if not multi == OK:
            raise ValueError("Got '{multi}' from MULTI instead of '{OK}' ")

        if isinstance(transaction_error := replies, Exception):
            causes = [(i, resp) for i, resp in enumerate(acks) if not resp == QUEUED]
            output = [transaction_error for _ in self._commands]
            for i, cause in causes:
                output[i] = cause
            return output

        assert len(replies) == len(self._commands), "Got wrong number of replies from transaction"
        return [cmd._parse_response(reply) for cmd, reply in zip(self._commands, replies)]
