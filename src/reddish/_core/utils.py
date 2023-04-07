from __future__ import annotations

import json
from itertools import islice
from typing import Iterable, Generator, Tuple, Union

from pydantic.json import pydantic_encoder


def partition(
    iterable: Iterable, lenghts: Iterable[int]
) -> Generator[Tuple, None, None]:
    iterator = iter(iterable)
    for length in lenghts:
        yield tuple(islice(iterator, length))


def json_dumps(data):
    return json.dumps(data, default=pydantic_encoder)


def strip_whitespace(template_string: str) -> str:
    return " ".join(template_string.split())


def get_subcommand(command, index: int) -> Union[str, None]:
    try:
        part = command._parts[index]
    except IndexError:
        return None
    else:
        if isinstance(part, str):
            return part.upper()
        else:
            return None
