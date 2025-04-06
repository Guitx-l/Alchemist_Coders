import rsk
import abc
import sys
import argparse
import numpy as np
from colorama import Fore, init
from datetime import datetime
from typing import Literal, Any, Sequence, Type

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



class BaseClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        self.client = client
        self.logger: Logger = Logger(self.__class__.__name__, True)
        self.referee: dict = self.client.referee

    @abc.abstractmethod
    def goal_sign(self) -> Literal[1, -1]:
        pass

    @abc.abstractmethod
    def update(self) -> None:
        pass

    @abc.abstractmethod
    def startup(self) -> None:
        pass

    @abc.abstractmethod
    def on_pause(self) -> None:
        pass

    @property
    def ball(self) -> array:
        return self.client.ball

    def is_inside_defense_zone(self, pos: Sequence[float]) -> bool:
        if self.goal_sign() == 1:
            return is_inside_left_zone(pos)
        return is_inside_right_zone(pos)



def start_client(MainClass: Type[BaseClient], RotatedClass: Type[BaseClient], args: list[str] | None = None):
    arguments = get_parser("Script that runs a client (adapted to halftime change)").parse_args(sys.argv[1::] if args is None else args)
    logger = Logger("client_loader", True)
    logger.info(f"args: {arguments}")
    team = arguments.team
    rotated: bool = arguments.rotated

    with rsk.Client(host=arguments.host, key=arguments.key) as c:  # tkt c un bordel mais touche pas ca marche nickel
        client = MainClass(c, team) if not rotated else RotatedClass(c, team)
        halftime = True
        pause = True
        client.startup()
        while True:
            if c.referee['halftime_is_running']:
                if halftime:
                    client = RotatedClass(c, team) if not rotated else MainClass(c, team)
                    logger.info(f"halftime, changing into {client.__class__}")
                    rotated = not rotated
                    halftime = False
            else:
                halftime = True
            if c.referee["game_paused"]:
                if pause:
                    client.on_pause()
                    pause = False
            else:
                pause = True

            try:
                client.update()
            except rsk.client.ClientError as e:
                if arguments.verbose:
                    client.logger.warn(e)


if __name__ == "__main__":
    pass
