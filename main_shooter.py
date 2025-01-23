import random
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


def log(message: object, str_type: Literal['info', 'debug', 'warn', 'error', 0, 1, 2, 3] = 'info') -> None:
    date = datetime.now().strftime('%H:%M:%S')
    if str_type in (0, 'info'):
        print(f"[{Fore.WHITE}INFO{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}")
    elif str_type in (1, 'debug'):
        print(f"[{Fore.GREEN}DEBUG{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}")
    elif str_type in (2, 'warn'):
        print(f"[{Fore.YELLOW}WARNING{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}")
    elif str_type in (3, 'error'):
        print(f"[{Fore.RED}ERROR{Fore.RESET}] ({Fore.LIGHTBLACK_EX}{date}{Fore.RESET}): {message}")


class MainClient:
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.referee: util.RefereeType = self.client.referee

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
                self.shooter.goto((*pos, angle), wait=True)
            else:
                self.shooter.goto(attack.get_shoot_pos(goal_pos, ball, 1.2), wait=True)
            self.shooter.goto(attack.get_shoot_pos(goal_pos, ball), wait=False)
            self.shooter.kick(1)
        else:
            self.shooter.goto(self.shooter.pose)


if __name__ == "__main__":
    with rsk.Client() as c: # tkt c un bordel mais touche pas ca marche nickel
        team = 'blue'#sys.argv[1]
        rotated = False#True if sys.argv[2].capitalize() == 'True' else False
        main = MainClient(c, team) if not rotated else RotatedClient(c, team)
        halftime = True
        while True:
            try:
                if c.referee['halftime_is_running']:
                    main = RotatedClient(c, team) if not rotated else MainClient(c, team)
                    if halftime:
                        rotated = not rotated
                        log(f"halftime, changing into {main.__class__} with team {team}")
                        halftime = False
                else:
                    halftime = True
                main.update()
            except KeyboardInterrupt:
                break
            except rsk.client.ClientError as e:
                if main.referee["teams"][main.shooter.color]["robots"][str(main.shooter.number)]["preemption_reasons"]:
                    continue
                if e.__repr__()[0] != "#":
                    log(e, 'info')
