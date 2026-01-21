import rsk
import sys
import argparse
from typing import Literal, Callable
from .log import getLogger
from src.bot import BotData

def get_parser(desc: str) -> argparse.ArgumentParser:
    """
    :param desc: description of the parser
    :return: an argparse parser that can be used to launch more easily the program, run get_parser().print_help()
    or check the argparse docs for more info
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-t', '--team', type=str, choices=('blue', 'green'), default='blue', help="team of the shooter (either 'blue' as default or 'green')")
    parser.add_argument('-H', '--host', type=str, default="127.0.0.1", help="host of the client, localhost by default")
    parser.add_argument('-k', '--key', type=str, default="", help="key of the client, empty by default")
    parser.add_argument('-v', '--verbose', action='store_true', help="if specified, the client will print all the warnings, not only the important ones")
    return parser

def start_client(DataClass: Callable[[rsk.Client, Literal['green', 'blue']], BotData], update_func: Callable[[BotData], None]) -> None:
    """
    Takes one class/function/object returning a BotData object and runs update_func automatically without any further intervention, even during the halftime.
    :param ClientClass: Callable returning BotData type object.
    :param update_func: function that will be called every "frame" with the BotData object as argument.
    """
    arguments = get_parser("Script that runs a client (adapted to halftime change)").parse_args(sys.argv[1::])
    logger = getLogger("client_loader")
    logger.info(f"args: {arguments}")
    team = arguments.team

    with rsk.Client(host=arguments.host, key=arguments.key) as c:  # tkt c un bordel mais touche pas ca marche nickel
        data = DataClass(c, team)
        while True:
            try:
                update_func(data)
            except rsk.client.ClientError as e:
                if arguments.verbose and str(e)[0] != "#":
                    data.logger.warning(e)