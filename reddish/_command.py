from typing import Any
from ._parser import parse, ParseError
from ._utils import to_bytes, json_dumps

class Command:
    """Class for specifing a single redis command"""

    def __init__(self, *args, **kwargs):
        """Accepts strings and data to form a redis command"""
        self._model = Any
        try:
            self._parts = self._make(*args, **kwargs)
        except TypeError as error:
            raise error from None

    def _make(self, *args):
        """Method for overriding in custom command classes"""
        return args

    def __repr__(self):
        parts = ((part if isinstance(part, (str, bytes)) else f'`{part}`' for part in self._parts))
        return f"""Command("{' '.join(parts)}")"""

    def into(self, model, /):
        """Parse the reponse into the provided type"""
        self._model = model
        return self

    def _parse_response(self, response):
        if self._model is Any:  # skip parsing
            return response
        if isinstance(response, Exception):
            return response
        try:
            return parse(self._model, response)
        except ParseError as error:
            return error

    def _dump_parts(self):
        parts = []
        for part in self._parts:
            if isinstance(part, (str, bytes)):
                parts.append(to_bytes(part))
            else:
                parts.append(to_bytes(json_dumps(part)))

        return parts

    def _dump(self):
        return [self._dump_parts()]

