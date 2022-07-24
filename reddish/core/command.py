from __future__ import annotations
from collections.abc import Iterator, Iterable, Mapping
from itertools import chain
from copy import copy

from typing import Union

from reddish._parser import parse, ParseError
from reddish._utils import to_bytes, to_resp_array, strip_whitespace
from reddish._templating import apply_template


AtomicType = Union[int, float, str, bytes]


class Args:
    """Container for data to be inlined into a `Command`."""

    def __init__(self, iterable: Iterable[AtomicType]) -> None:
        """Inline data to from an iterable collection such as list, tuple etc.

        Args:
            iterable: collection of data to be inlined
        """
        self._parts = []
        for part in iterable:
            if not isinstance(part, (int, float, str, bytes)):
                raise ValueError(f"''{repr(part)} is not a valid argument")
            self._parts.append(part)

    def __iter__(self) -> Iterator[bytes]:
        for part in self._parts:
            yield to_bytes(part)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}([{', '.join(repr(part) for part in self._parts)}])"

    @classmethod
    def from_dict(cls, mapping: Mapping[AtomicType, AtomicType]) -> Args:
        """Inline keys and values from a dict or other mapping.

        Args:
            mapping: dict or other mapping to inline keys and values from
        """
        if not isinstance(mapping, Mapping):
            raise ValueError('Value is not a Mapping')
        return cls(chain.from_iterable(mapping.items()))


class Command:
    """A redis command that can be executed against redis"""

    def __init__(self, template: str, *args: AtomicType, **kwargs: AtomicType) -> None:
        """Create redis command from template and data.

        Args:
            template: A template string for the command that may contain
                positional and keyword fields.
            *args: Positional fields
            **kwargs: Keyword fields
        """
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

        self._models: tuple[type, ...] = ()

    def into(self, model: type) -> Command:
        """Create a new command with a type for parsing a response.

        Args:
            model: type for the reponse to be parsed into

        Returns:
            A copy of the original command with the type for reponse parsing added
        """
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

    def __repr__(self) -> str:
        return self._repr

    def __bytes__(self):
        parts = []
        for part in self._parts:
            if isinstance(part, Args):
                for sub_part in part:
                    parts.append(sub_part)
            else:
                parts.append(to_bytes(part))
        return to_resp_array(*parts)
