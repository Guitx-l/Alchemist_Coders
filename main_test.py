import logging
import rsk
import attack
import numpy as np
from rsk import constants
import time
import math
import cconstans
import util
from typing import Any, Literal
import datetime
from colorama import Fore


def log(message: object, str_type: Literal['info', 'debug', 'warn', 'error'] = 'info') -> None:
    date = datetime.datetime.now().strftime('%H:%M:%S')
    if str_type in (0, 'info'):
        print(f"[INFO] ({date}): {message}")
    elif str_type in (1, 'debug'):
        print(f"{Fore.GREEN}[DEBUG] ({date}): {message}")
    elif str_type in (2, 'warn'):
        print(f"{Fore.YELLOW}[WARNING] ({date}): {message}")
    elif str_type in (3, 'error'):
        print(f"{Fore.RED}[ERROR] ({date}): {message}")


class Main:
    def __init__(self, client: rsk.Client):
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.blue1
        self.defender = client.blue2
        self.referee: dict = self.client.referee
        self.logger = logging.getLogger(__name__)

    def is_preempted(self, robot: rsk.client.ClientRobot) -> bool:
        return self.referee["teams"][robot.team]["robots"][str(robot.number)]["preempted"]

    def startup(self) -> None:
        log(f"STARTUP ({str(time.time()).split('.')[1]})")
        if not self.is_preempted(self.shooter):
            self.shooter.goto((-0.15, 0, 0))

    def main(self) -> None:
        ball = self.client.ball.copy() if self.client.ball is not None else np.array([0, 0])
        if 0.2 < ball[0] and util.is_inside_court(ball) and not self.is_preempted(self.shooter):
            if ball[0] < self.shooter.position[0]:
                ball_vector = self.shooter.position - ball
                length = math.sqrt(np.sum(np.power(ball_vector, np.array([2, 2]))))
                ball_vector = ball_vector / length # normalize
                ball_vector[0] *= -1
                pos = ball + ball_vector * cconstans.shooter_offset
                self.shooter.goto((*pos, math.atan2(-ball_vector[1], -ball_vector[0])))

            self.shooter.goto(attack.get_shoot_pos(cconstans.goal_pos, ball, 1.2), wait=True)
            self.shooter.goto(attack.get_shoot_pos(cconstans.goal_pos, ball), wait=False)
            self.shooter.kick(1)
        else:
            self.shooter.goto(self.shooter.pose)


if __name__ == "__main__":
    with rsk.Client() as c:
        main = Main(c)
        main.startup()
        while True:
            try:
                main.main()
            except KeyboardInterrupt:
                break
