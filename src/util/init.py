import rsk
import sys
import argparse
from typing import Callable
from .log import getLogger


def get_parser(desc: str) -> argparse.ArgumentParser:
    """
    :param desc: description du parseur
    :return: un parseur argparse qui peut être utilisé pour lancer plus facilement le programme, exécuter get_parser().print_help()
    ou consulter la documentation argparse pour plus d'informations
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-t', '--team', type=str, choices=('blue', 'green'), default='blue', help="team of the shooter (either 'blue' as default or 'green')")
    parser.add_argument('-H', '--host', type=str, default="127.0.0.1", help="host of the client, localhost by default")
    parser.add_argument('-k', '--key', type=str, default="", help="key of the client, empty by default")
    parser.add_argument('-v', '--verbose', action='store_true', help="if specified, the client will print all the warnings, not only the important ones")
    return parser


def start_client(update_func: Callable[[rsk.Client, str, int, dict], None], number: int, data_dict: dict) -> None:
    """
    :description: Prend une classe/fonction/objet retournant un data_dict et exécute update_func automatiquement sans intervention supplémentaire.
    :param update_func: fonction qui sera appelée à chaque "frame" avec l'objet data_dict comme argument.
    :param number: numéro du robot à contrôler (1 ou 2)
    :param data_dict: dictionnaire qui sera passé à update_func comme argument
    """
    arguments = get_parser("Script that runs a client (adapted to halftime change)").parse_args(sys.argv[1::])
    logger = getLogger("client_loader")
    logger.info(f"args: {arguments}")
    team = arguments.team
    if 'logger' not in data_dict.keys():
        data_dict['logger'] = logger

    with rsk.Client(host=arguments.host, key=arguments.key) as client:  # tkt c un bordel mais touche pas ca marche nickel
        while True:
            try:
                update_func(client, team, number, data_dict)
            except rsk.client.ClientError as e:
                    data_dict['logger'].warning(e)