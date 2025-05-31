import time
import argparse
import numpy as np
import rsk
import math
import pynput
import sys

changed = False

def get_parser(desc: str) -> argparse.ArgumentParser:
    """
    :param desc: description of the parser
    :return: an argparse parser that can be used to launch more easily the program, run get_parser().print_help()
    or check the argparse docs for more info
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-r', '--rotated', action='store_true', help="the game will start with the rotated client if specified")
    parser.add_argument('-t', '--team', type=str, choices=('blue', 'green'), default='blue', help="team of the shooter (either 'blue' as default or 'green')")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')
    return parser


def angle_of(pos) -> float:
    return math.atan2(pos[1], pos[0])

def on_press(key):
    with rsk.Client() as client:
        print(client.referee)

if __name__ == '__main__':
    team = get_parser("").parse_args().team
    with rsk.Client() as client:
        print(client.referee)
        if  team == "green":
            en_color = "blue"
        else :
            en_color = "green"

        score_diff = client.referee["teams"][en_color]["score"] - client.referee["teams"][team]["score"]
        if score_diff <= 3 and changed == False:
            # code sans changement de rôle

            pass
        else:
            changed = True
            # code avec chgt de rôle

