from typing import Generic, TypeVar, overload, Iterator, Any
from .command import Command

T = TypeVar("T", covariant=True)
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")

class MultiExec(Generic[T]):
    @overload  # one arg
    def __init__(self: "MultiExec[tuple[T1]]", c1: Command[T1]) -> None: ...
    # (empty) comment after definition to keep black from removing newlines

    @overload  # two args
    def __init__(
        self: "MultiExec[tuple[T1, T2]]", c1: Command[T1], c2: Command[T2]
    ) -> None: ...
    #

    @overload  # three args
    def __init__(
        self: "MultiExec[tuple[T1, T2, T3]]",
        c1: Command[T1],
        c2: Command[T2],
        c3: Command[T3],
    ) -> None: ...
    #

    @overload  # four args
    def __init__(
        self: "MultiExec[tuple[T1, T2, T3, T4]]",
        c1: Command[T1],
        c2: Command[T2],
        c3: Command[T3],
        c4: Command[T4],
    ) -> None: ...
    #

    @overload  # five args
    def __init__(
        self: "MultiExec[tuple[T1, T2, T3, T4, T5]]",
        c1: Command[T1],
        c2: Command[T2],
        c3: Command[T3],
        c4: Command[T4],
        c5: Command[T5],
    ) -> None: ...
    #

    @overload  # more than five homogenous args
    def __init__(self: MultiExec[tuple[T1, ...]], *commands: Command[T1]) -> None: ...
    #

    @overload  #  more than five inhomogenous args
    def __init__(self: MultiExec[tuple], *commands: Command) -> None: ...
    #

    def __bytes__(self) -> bytes: ...
    def __repr__(self) -> str: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Command]: ...
    def _parse_response(self, *responses: Any) -> T: ...
