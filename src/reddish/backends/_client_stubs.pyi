from reddish._core.command import Command
from reddish._core.multiexec import MultiExec
from typing import Union, TypeVar, overload, Any

T = TypeVar("T", covariant=True)

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")

CommandType = Union[Command[T], MultiExec[T]]

class SyncRedis:
    def execute(self, command: CommandType[T]) -> T: ...
    # (empty) comment after definition to keep black from removing newlines

    @overload
    def execute_many(self, c1: CommandType[T1]) -> tuple[T1]: ...
    #

    @overload
    def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
    ) -> tuple[T1, T2]: ...
    #

    @overload
    def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
        c3: CommandType[T3],
    ) -> tuple[T1, T2, T3]: ...
    #

    @overload
    def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
        c3: CommandType[T3],
        c4: CommandType[T4],
    ) -> tuple[T1, T2, T3, T4]: ...
    #

    @overload
    def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
        c3: CommandType[T3],
        c4: CommandType[T4],
        c5: CommandType[T5],
    ) -> tuple[T1, T2, T3, T4, T5]: ...
    #

    @overload
    def execute_many(
        self,
        *commands: CommandType[T],
    ) -> tuple[T, ...]: ...

class AsyncRedis:
    async def execute(self, command: CommandType[T]) -> T: ...
    #

    @overload
    async def execute_many(self, c1: CommandType[T1]) -> tuple[T1]: ...
    #

    @overload
    async def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
    ) -> tuple[T1, T2]: ...
    #

    @overload
    async def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
        c3: CommandType[T3],
    ) -> tuple[T1, T2, T3]: ...
    #

    @overload
    async def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
        c3: CommandType[T3],
        c4: CommandType[T4],
    ) -> tuple[T1, T2, T3, T4]: ...
    #

    @overload
    async def execute_many(
        self,
        c1: CommandType[T1],
        c2: CommandType[T2],
        c3: CommandType[T3],
        c4: CommandType[T4],
        c5: CommandType[T5],
    ) -> tuple[T1, T2, T3, T4, T5]: ...
    #

    @overload
    async def execute_many(
        self,
        *commands: CommandType[T],
    ) -> tuple[T, ...]: ...
