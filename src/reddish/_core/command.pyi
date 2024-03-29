from typing import Generic, TypeVar, overload, Type, Any, Iterable, Iterator, Mapping

AtomicType = int | float | str | bytes

class Args:
    def __init__(self, iterable: Iterable[AtomicType]) -> None: ...
    def __iter__(self) -> Iterator[AtomicType]: ...
    def __repr__(self) -> str: ...
    @classmethod
    def from_dict(cls, mapping: Mapping[AtomicType, AtomicType]) -> Args: ...

C = TypeVar("C", covariant=True)
T = TypeVar("T")

class Command(Generic[C]):
    def __init__(
        self, cmd: str, *args: AtomicType | Args, **kwargs: AtomicType | Args
    ) -> None: ...
    @overload
    def into(self: "Command[C]", type: Type[T]) -> "Command[T]": ...
    @overload
    def into(self: "Command[C]", type: None) -> "Command[None]": ...
    def _parse_response(self, response: Any) -> C: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __bytes__(self) -> bytes: ...
