import random
import sys
import time
import argparse
import rsk
import numpy as np
import math
import cconstans
import util
from typing import Literal
from datetime import datetime
from colorama import Fore
from pygame import Vector2


def get_shoot_pos(goal_pos: np.ndarray, ball_pos: np.ndarray, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    #finding the shooter pos
    ball_to_goal_vec = goal_pos - ball_pos
    shooter_pos: np.ndarray = ball_to_goal_vec * -shooter_offset_scale + goal_pos
    return (*shooter_pos, math.atan2(*reversed(ball_to_goal_vec)))


def log(message: object, str_type: Literal['info', 'debug', 'warn', 'error', 0, 1, 2, 3] = 'info', **kwargs) -> None:
    date = datetime.now().strftime('%H:%M:%S')
    kwargs = {"end":"\n"} | kwargs
    color = Fore.WHITE
    reset = Fore.RESET
    type: str = "INFO"
    if str_type in (1, 'debug'):
        color = Fore.GREEN; type = "DEBUG"
    elif str_type in (2, 'warn'):
        color = Fore.YELLOW; type = "WARNING"
    elif str_type in (3, 'error'):
        color = Fore.RED; type = "ERROR"
    print(f"[{color}{type}{reset}] [{Fore.CYAN}{__name__}{reset}] ({Fore.LIGHTBLACK_EX}{date}{reset}) - {color}{message}{reset}", **kwargs)

class MainClient:
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.referee: util.RefereeType = self.client.referee
        self.last_ball_overlap: float = time.time()
        self.goal_pos = np.array([cconstans.goal_pos[0], random.random() * 0.6 - 0.3])

    def on_pause(self) -> None:
        self.goal_pos = np.array([cconstans.goal_pos[0], random.random() * 0.6 - 0.3])

    def startup(self):
        log(f"Main startup ({str(time.time()).split('.')[1]})")

    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        ball = self.client.ball

        if util.is_inside_circle(self.shooter.position, ball, rsk.constants.timed_circle_radius):
            if time.time() - self.last_ball_overlap >= cconstans.timed_circle_timeout:
                pass
        else:
            self.last_ball_overlap = time.time()

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
                self.shooter.goto(get_shoot_pos(goal_pos, ball, 1.2), wait=True)
            self.shooter.goto(get_shoot_pos(goal_pos, ball), wait=False)
            if util.is_inside_circle(self.shooter.position, ball, .15):
                self.shooter.kick(1)
        else:
            self.shooter.goto(self.shooter.pose)



class RotatedClient:
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.referee: util.RefereeType = self.client.referee
        self.last_ball_overlap: float = time.time()
        self.goal_pos = np.array([-cconstans.goal_pos[0], random.random() * 0.6 - 0.3])

    def on_pause(self) -> None:
        self.goal_pos = np.array([-cconstans.goal_pos[0], random.random() * 0.6 - 0.3])

    def startup(self) -> None:
        log(f"Rotated startup ({str(time.time()).split('.')[1]})")

    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        ball = self.client.ball

        if util.is_inside_circle(self.shooter.position, ball, rsk.constants.timed_circle_radius):
            if time.time() - self.last_ball_overlap >= cconstans.timed_circle_timeout:
                pass
        else:
            self.last_ball_overlap = time.time()

        if -cconstans.shooter_offset > ball[0] > -rsk.constants.field_length/2 + rsk.constants.defense_area_length and util.is_inside_court(ball):
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
                log("ball behind", 'debug')
            else:
                self.shooter.goto(get_shoot_pos(self.goal_pos, ball, 1.15), wait=True)
                log("moving straight to ball", 'debug')
            self.shooter.goto(get_shoot_pos(self.goal_pos, ball), wait=False)
            if util.is_inside_circle(self.shooter.position, ball, .15):
                self.shooter.kick(1)
                log(f"shooting to {np.around(self.goal_pos, 2)} from {np.around(self.shooter.pose, 2)}")
        else:
            self.shooter.goto(self.shooter.pose)


def main(args: str | None = None):
    arguments = util.get_parser("Script that runs the shooter (adapted to halftime change)").parse_args(sys.argv[1::] if args is None else args)
    log(f"args: {arguments}")
    team: str = arguments.team
    rotated: bool = arguments.rotated

    with rsk.Client() as c:  # tkt c un bordel mais touche pas ca marche nickel
        shooter_client = MainClient(c, team) if not rotated else RotatedClient(c, team)
        halftime = True
        pause = True
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
                if c.referee["game_paused"]:
                    if pause:
                        shooter_client.on_pause()
                        log(f"running {shooter_client.__class__}.{shooter_client.on_pause.__name__}...")
                        pause = False
                else:
                    pause = True
            except KeyboardInterrupt:
                break
            try:
                shooter_client.update()
            except rsk.client.ClientError:
                continue


if __name__ == "__main__":
    main()
