import abc
import rsk
import attack
import numpy as np
from rsk import constants
import time
import math
import cconstans
import util
from typing import Literal, final
import datetime
from colorama import Fore
from pygame import Vector2
import sys


def log(message: object, str_type: Literal['info', 'debug', 'warn', 'error', 0, 1, 2, 3] = 'info') -> None:
    date = datetime.datetime.now().strftime('%H:%M:%S')
    if str_type in (0, 'info'):
        print(f"{Fore.GREEN}[INFO] ({date}): {message}")
    elif str_type in (1, 'debug'):
        print(f"{Fore.CYAN}[DEBUG] ({date}): {message}")
    elif str_type in (2, 'warn'):
        print(f"{Fore.YELLOW}[WARNING] ({date}): {message}")
    elif str_type in (3, 'error'):
        print(f"{Fore.RED}[ERROR] ({date}): {message}")


class IClient(abc.ABC):
    @final
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter = client.robots[team][1]
        self.referee: util.RefereeType = self.client.referee

    def is_preempted(self, robot: rsk.client.ClientRobot) -> bool:
        return self.referee["teams"][robot.team]["robots"][str(robot.number)]['preempted']

    def is_penalized(self, robot: rsk.client.ClientRobot) -> bool:
        return self.referee['teams'][robot.team]['robots'][str(robot.number)]['penalized']

    def can_play(self, robot: rsk.client.ClientRobot) -> bool:
        return (not self.is_preempted(robot)) and (not self.is_penalized(robot))

    @abc.abstractmethod
    def startup(self) -> None: ...
    @abc.abstractmethod
    def update(self) -> None: ...


class MainClient(IClient):
    def startup(self) -> None:
        log(f"STARTUP")
        if not self.can_play(self.shooter):
            self.shooter.goto((-0.15, 0, 0))

    def update(self) -> None:
        ball = self.client.ball.copy() if self.client.ball is not None else np.array([0, 0])

        if 0.1 < ball[0] and util.is_inside_court(ball) and self.can_play(self.shooter):
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
                self.shooter.goto(attack.get_shoot_pos(cconstans.goal_pos, ball, 1.2), wait=True)
            self.shooter.goto(attack.get_shoot_pos(cconstans.goal_pos, ball), wait=False)
            self.shooter.kick(1)
        else:
            self.shooter.goto(self.shooter.pose)

class RotatedClient(IClient):
    def startup(self) -> None:
        pass

    def update(self) -> None:
        pass


if __name__ == "__main__":
    with rsk.Client() as c:
        team = sys.argv[1]
        rotated = True if sys.argv[2].capitalize() == 'True' else False
        main = MainClient(c, team)
        if rotated:
            main = RotatedClient(c, team)
        main.startup()
        log(type(main), 'debug')
        while True:
            try:
                if c.referee['halftime_is_running']:
                    main = RotatedClient(c, team)
                    if rotated:
                        main = MainClient(c, team)
                main.update()
            except KeyboardInterrupt:
                break
