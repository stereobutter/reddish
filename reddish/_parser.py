from pydantic import Json
from typing import Union, Optional, GenericAlias, _UnionGenericAlias
from collections.abc import Mapping, Iterable

generic_aliases = (GenericAlias, _UnionGenericAlias)


def apply_parsing_rules(type_):
    if type_ is str:
        return Union[Json[str], str]  # Json[str] parses b'"hello"' as 'hello'

    elif type_ is type(None):
        return Union[None, Json[None]]  #Json[None] parses b'null' as None

    elif isinstance(type_, generic_aliases):
        origin = type_.__origin__
        args = type_.__args__

        if origin is Union:
            args = tuple(apply_parsing_rules(t) for t in args)
            return Union[args]

        elif origin is Optional:  # type: ignore
            return apply_parsing_rules(Union[(None, *args)])
        elif issubclass(origin, Mapping):
            key_type, value_type = args
            return Union[
                origin[apply_parsing_rules(key_type), apply_parsing_rules(value_type)],
                type_,
                Json[type_]
                ]
        elif issubclass(origin, Iterable):
            elem_type = args[0]
            return Union[
                origin[apply_parsing_rules(elem_type)],
                type_,
                Json[type_]
                ]
    else:
        return Union[type_, Json[type_]]