from reddish._core.command import Command
from reddish._core.multiexec import MultiExec
from typing_extensions import assert_type


def check_Command() -> None:
    assert_type(Command("...").into(str), Command[str])
    assert_type(Command("...").into(str | int), Command[int | str])
    assert_type(Command("...").into(list[str]), Command[list[str]])


def check_MultiExec_one_arg() -> None:
    assert_type(
        MultiExec(
            Command("...").into(str),
        ),
        MultiExec[tuple[str]],
    )


def check_MultiExec_two_arg() -> None:
    assert_type(
        MultiExec(
            Command("...").into(str),
            Command("...").into(int),
        ),
        MultiExec[tuple[str, int]],
    )


def check_MultiExec_three_arg() -> None:
    assert_type(
        MultiExec(
            Command("...").into(str),
            Command("...").into(int),
            Command("...").into(float),
        ),
        MultiExec[tuple[str, int, float]],
    )


def check_MultiExec_four_arg() -> None:
    assert_type(
        MultiExec(
            Command("...").into(str),
            Command("...").into(int),
            Command("...").into(float),
            Command("...").into(str),
        ),
        MultiExec[tuple[str, int, float, str]],
    )


def check_MultiExec_five_arg() -> None:
    assert_type(
        MultiExec(
            Command("...").into(str),
            Command("...").into(int),
            Command("...").into(float),
            Command("...").into(str),
            Command("...").into(bytes),
        ),
        MultiExec[tuple[str, int, float, str, bytes]],
    )


def check_MultiExec_n_args_uniform() -> None:
    str_cmd = Command("...").into(str)
    assert_type(
        MultiExec(str_cmd, str_cmd, str_cmd, str_cmd, str_cmd, str_cmd),
        MultiExec[tuple[str, ...]],
    )


def check_MultiExec_n_args_non_uniform() -> None:
    assert_type(
        MultiExec(
            Command("...").into(str),
            Command("...").into(int),
            Command("...").into(float),
            Command("...").into(str),
            Command("...").into(bytes),
            Command("...").into(bytes),
        ),
        MultiExec[tuple],
    )
