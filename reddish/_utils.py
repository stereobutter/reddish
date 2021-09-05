from typing import Union, Iterable
from pydantic.json import pydantic_encoder
import json

def to_bytes(arg: Union[str, bytes]):
    if isinstance(arg, bytes):
        return arg
    elif isinstance(arg, str):
        return arg.encode('utf-8')
    else:
        raise TypeError(f"'{arg}' cannot be cast into bytes.")


def json_dumps(data):
    return json.dumps(data, default=pydantic_encoder)