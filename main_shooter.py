import random
import sys
import time
import argparse
import rsk
import attack
import numpy as np
import math
import cconstans
import util
from typing import Literal
from datetime import datetime
from colorama import Fore
from pygame import Vector2


def log(message: object, str_type: Literal['info', 'debug', 'warn', 'error', 0, 1, 2, 3] = 'info', **kwargs) -> None:
    date = datetime.now().strftime('%H:%M:%S')
    kwargs = {"end":"\n"} | kwargs
    if str_type in (0, 'info'):
        print(f"[{Fore.WHITE}INFO{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}", **kwargs)
    elif str_type in (1, 'debug'):
        print(f"[{Fore.GREEN}DEBUG{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}", **kwargs)
    elif str_type in (2, 'warn'):
        print(f"[{Fore.YELLOW}WARNING{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}", **kwargs)
    elif str_type in (3, 'error'):
        print(f"[{Fore.RED}ERROR{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}", **kwargs)


class MainClient:
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.referee: util.RefereeType = self.client.referee

    def startup(self):
        log(f"Main startup ({str(time.time()).split('.')[1]})")

    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        ball = self.client.ball

        if cconstans.shooter_offset < ball[0] < rsk.constants.field_length/2 - rsk.constants.defense_area_length and util.is_inside_court(ball):
            goal_pos = np.array([cconstans.goal_pos[0], random.random() * 0.6 - 0.3])
            if ball[0] < self.shooter.position[0]:
                ball_vector = Vector2(*(self.shooter.position - ball))
                ball_vector.x *= -1
                pos = ball + ball_vector.normalize() * cconstans.shooter_offset
                angle = math.atan2(-ball_vector.y, -ball_vector.x)
                if 0 <= math.degrees(angle) < 35:
                    pos = ball + (Vector2(-1, -1).normalize() * (cconstans.shooter_offset + .1))
                elif -35 < math.degrees(angle) < 0:
                    pos = ball + (Vector2(-1, 1).normalize() * (cconstans.shooter_offset + .1))
                self.shooter.goto((*pos, angle), wait=True)
            else:
                self.shooter.goto(attack.get_shoot_pos(goal_pos, ball, 1.2), wait=True)
            self.shooter.goto(attack.get_shoot_pos(goal_pos, ball), wait=False)
            self.shooter.kick(1)
        else:
            self.shooter.goto(self.shooter.pose)



class RotatedClient:
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.referee: util.RefereeType = self.client.referee

    def startup(self):
        log(f"Rotated startup ({str(time.time()).split('.')[1]})")

    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        ball = self.client.ball

        if -cconstans.shooter_offset > ball[0] > -rsk.constants.field_length/2 + rsk.constants.defense_area_length and util.is_inside_court(ball):
            goal_pos = np.array([-cconstans.goal_pos[0], random.random() * 0.6 - 0.3])
            if ball[0] > self.shooter.position[0]:
                ball_vector = Vector2(*(self.shooter.position - ball))
                ball_vector.x *= -1
                pos = ball + ball_vector.normalize() * cconstans.shooter_offset
                angle = math.atan2(ball_vector.y, ball_vector.x)
                if 0 <= math.degrees(angle) < 35:
                    pos = ball + (Vector2(1, 1).normalize() * (cconstans.shooter_offset + .1))
                elif -35 < math.degrees(angle) < 0:
                    pos = ball + (Vector2(1, -1).normalize() * (cconstans.shooter_offset + .1))
                self.shooter.goto((*pos, -angle), wait=True)
            else:
                self.shooter.goto(attack.get_shoot_pos(goal_pos, ball, 1.2), wait=True)
            self.shooter.goto(attack.get_shoot_pos(goal_pos, ball), wait=False)
            self.shooter.kick(1)
            log(f"shooting to {np.around(goal_pos, 2)} from {np.around(self.shooter.pose, 2)}")
        else:
            self.shooter.goto(self.shooter.pose)


def main(args: str | None = None):
    parser = argparse.ArgumentParser(description="Script that runs the shooter (adapted to halftime change)")
    parser.add_argument('-r', '--rotated', type=bool, default=False, help="if true, the game will start with the rotated client")
    parser.add_argument('-t', '--team', type=str, default='blue', help="decides the team of the shooter, either 'blue' or 'green'")
    parser.add_argument('-v', '--verbose', action='store_true')
    arguments: argparse.Namespace = parser.parse_args(sys.argv[1::] if args is None else args)
    log(f"args: {arguments}")
    team: str = arguments.team
    rotated: bool = arguments.rotated

    with rsk.Client() as c:  # tkt c un bordel mais touche pas ca marche nickel
        shooter_client = MainClient(c, team) if not rotated else RotatedClient(c, team)
        halftime = True
        shooter_client.startup()
        while True:
            try:
                if c.referee['halftime_is_running']:
                    if halftime:
                        shooter_client = RotatedClient(c, team) if not rotated else MainClient(c, team)
                        log(f"halftime, changing into {shooter_client.__class__}")
                        rotated = not rotated
                        halftime = False
                else:
                    halftime = True
            except KeyboardInterrupt:
                break
            try:
                shooter_client.update()
            except rsk.client.ClientError:
                continue


if __name__ == "__main__":
    main()
