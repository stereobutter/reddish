from reddish._core.errors import UnsupportedCommandError
from reddish._core.utils import get_subcommand

UNSUPPORTED_COMMANDS = (
    "SUBSCRIBE",
    "UNSUBSCRIBE",
    "PSUBSCRIBE",
    "PUNSUBSCRIBE",
    "SSUBSCRIBE",
    "SUNSUBSCRIBE",
    "MONITOR",
)


def disallow_client_tracking(command):
    subcommand = get_subcommand(command, 1)
    if subcommand == "TRACKING":
        raise UnsupportedCommandError("The 'CLIENT TRACKING' command is not supported.")


UNSUPPORTED_SUBCOMMANDS = {"CLIENT": disallow_client_tracking}


def check_for_unsupported_commands(command):
    name = command._command_name.upper()
    if name in UNSUPPORTED_COMMANDS:
        raise UnsupportedCommandError(f"'{command._command_name}' is not supported.")
    elif name in UNSUPPORTED_SUBCOMMANDS:
        check = UNSUPPORTED_SUBCOMMANDS[name]
        check(command)
