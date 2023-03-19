from .command import Command
from .multiexec import MultiExec
from typing import Union

CommandType = Union[Command, MultiExec]
