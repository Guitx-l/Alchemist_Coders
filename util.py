import rsk
import numpy as np
from typing import Literal, Any, Sequence
import argparse
from datetime import datetime
from colorama import Fore, init
init(autoreset=True)
type array = np.ndarray[(2, 1), np.dtype[Any]]

def is_inside_circle(point: array, center: array, radius: float) -> bool:
    return sum((center - point) ** 2) <= radius ** 2


def is_inside_rect(point: Sequence[float], bottomleft: Sequence[float], topright: Sequence[float]) -> bool:
    return bottomleft[0] <= point[0] <= topright[0] and bottomleft[1] <= point[1] <= topright[1]


def is_inside_court(x: Sequence[float]) -> bool:
    return -rsk.constants.field_length / 2 < x[0] < rsk.constants.field_length/2 and -rsk.constants.field_width / 2 < x[1] < rsk.constants.field_width/2


def is_inside_right_zone(x: Sequence[float]) -> bool:
    return x[0] >= rsk.constants.field_length/2 - rsk.constants.defense_area_length and rsk.constants.defense_area(True)[0][1] <= x[1] <= rsk.constants.defense_area(True)[1][1]


def is_inside_left_zone(x: Sequence[float]) -> bool:
    return x[0] <= -rsk.constants.field_length/2 + rsk.constants.defense_area_length and -rsk.constants.defense_area_width/2 <= x[1] <= rsk.constants.defense_area_width/2


def get_parser(desc: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-r', '--rotated', action='store_true', help="the game will start with the rotated client if specified")
    parser.add_argument('-t', '--team', type=str, choices=('blue', 'green'), default='blue', help="team of the shooter (either 'blue' as default or 'green')")
    parser.add_argument('-H', '--host', type=str, default="127.0.0.1", help="host of the client")
    parser.add_argument('-k', '--key', type=str, default="", help="key of the client")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')
    return parser

class Logger:
    def __init__(self, name: str, debug: bool, quiet: bool = False, verbose: bool = False):
        self.name = name
        self.enable_debug = debug
        self.quiet = quiet
        self.verbose = verbose

    def log(self, message: Any, str_type: Literal['info', 'debug', 'warn', 'error', 0, 1, 2, 3] = 'info', **kwargs) -> None:
        date = datetime.now().strftime('%H:%M:%S')
        kwargs = {"end": "\n"} | kwargs
        color = Fore.WHITE
        reset = Fore.RESET
        type: str = "INFO"
        if str_type in (1, 'debug'):
            color = Fore.GREEN
            type = "DEBUG"
        elif str_type in (2, 'warn'):
            color = Fore.YELLOW
            type = "WARNING"
        elif str_type in (3, 'error'):
            color = Fore.RED
            type = "ERROR"
        print(f"[{color}{type}{reset}] [{Fore.CYAN}{self.name}{reset}] ({Fore.LIGHTBLACK_EX}{date}{reset}) - {color}{message}{reset}", **kwargs)

    def info(self, message: Any, verbose: bool | None = None, **kwargs) -> None:
        self.log(message, 'info', **kwargs)

    def warn(self, message: Any, verbose: bool | None = None, **kwargs) -> None:
        self.log(message, 'warn', **kwargs)

    def error(self, message: Any, verbose: bool | None = None, **kwargs) -> None:
        self.log(message, 'error', **kwargs)

    def debug(self, message: Any, verbose: bool | None = None, **kwargs) -> None:
        if self.enable_debug:
            self.log(message, 'debug', **kwargs)

import enum
class MovementGoal(enum.IntEnum):
    BALL_BEHIND = 1
    SHOOT = -1
    REPOSITION = -2
    BALL_ABUSE = 2
    ABUSIVE_DEFENSE = 3

if __name__ == "__main__":
    print(
        MovementGoal.BALL_BEHIND,
        MovementGoal.SHOOT,
        MovementGoal.REPOSITION
    )
