import rsk
from typing import Iterable
import numpy as np
from typing import TypedDict, Literal, Any
import argparse
from datetime import datetime
from colorama import Fore, init
init(autoreset=True)


class Referee:
    def __init__(self, referee: dict):
        self.__dict__ = referee.copy()


class Robots:
    def __init__(self, robots: dict[str, dict]):
        self.robots = robots
        self.indexes = (
            ("green", 1),
            ("green", 2),
            ("blue", 1),
            ("blue", 2)
        )
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self) -> rsk.client.ClientRobot:
        self.index += 1
        if self.index > 3:
            raise StopIteration
        i = self.indexes[self.index]
        return self.robots[i[0]][i[1]]

    def __len__(self):
        return 4

    def __getitem__(self, item: int) -> rsk.client.ClientRobot:
        return self.robots[self.indexes[item][0]][self.indexes[item][1]]


def is_inside_circle(point: np.ndarray[float], center: np.ndarray[float], radius: float) -> bool:
    return sum((center - point) ** 2) <= radius ** 2


def is_inside_rect(point: Iterable[float], bottomleft: Iterable[float], topright: Iterable[float]) -> bool:
    return bottomleft[0] <= point[0] <= topright[0] and bottomleft[1] <= point[1] <= topright[1]


def is_inside_court(x: Iterable[float]) -> bool:
    return -rsk.constants.field_length / 2 < x[0] < rsk.constants.field_length/2 and -rsk.constants.field_width / 2 < x[1] < rsk.constants.field_width/2

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

if __name__ == "__main__":
    print({"A":1} | {"A":2})
