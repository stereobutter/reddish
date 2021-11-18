from collections.abc import Mapping
from itertools import chain
from copy import copy
from ._parser import parse, ParseError
from ._utils import to_bytes, to_resp_array, strip_whitespace
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

    def __repr__(self):
        return f"{self.__class__.__name__}([{', '.join(repr(part) for part in self._parts)}])"

    @classmethod
    def from_dict(cls, /, mapping):
        if not isinstance(mapping, Mapping):
            raise ValueError('Value is not a Mapping')
        return cls(chain.from_iterable(mapping.items()))


class Command:
    """Class for specifing a single redis command"""

    def __init__(self, template, *args, **kwargs):
        """Accepts strings and data to form a redis command"""
        normalized_template = strip_whitespace(template)
        self._parts = apply_template(normalized_template, *args, **kwargs)

        for part in self._parts:
            if not isinstance(part, (int, float, str, bytes, Args)):
                raise ValueError(f"'{repr(part)}' is not valid as part of a command")

        try:
            self._command_name = self._parts[0]
        except IndexError:
            raise ValueError('An empty template string is not a valid command')

        args_and_kwargs = (
            [repr(normalized_template)] +
            [repr(arg) for arg in args] +
            ["{}={}".format(key, repr(value)) for key, value in kwargs.items()]
        )
        self._repr = f"{self.__class__.__name__}({', '.join(args_and_kwargs)})"

        self._models = ()

    def __repr__(self):
        return self._repr

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

    def __len__(self):
        return 1

    def __bytes__(self):
        parts = []
        for part in self._parts:
            if isinstance(part, Args):
                for sub_part in part:
                    parts.append(sub_part)
            else:
                parts.append(to_bytes(part))
        return to_resp_array(*parts)


OK = b'OK'
QUEUED = b'QUEUED'


class MultiExec:
    """Class for wrapping commands into a redis MULTI and EXEC transaction"""

    _MULTI = to_resp_array(b'MULTI')
    _EXEC = to_resp_array(b'EXEC')

    def __init__(self, *commands: Command):
        self._commands = commands

    def __repr__(self):
        commands = (repr(cmd) for cmd in self._commands)
        return f"{self.__class__.__name__}({', '.join(commands)})"

    def __iter__(self):
        yield from self._commands

    def __len__(self):
        return 2 + len(self._commands)  # MULTI cmds... EXEC

    def __bytes__(self):
        commands = b''.join(bytes(cmd) for cmd in self._commands)
        return b'%b%b%b' % (self._MULTI, commands, self._EXEC)

    def _parse_response(self, *responses):
        assert len(responses) == len(self._commands) + 2, "Got wrong number of replies from pipeline"

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
