import random
import sys
import abc
import time
import rsk
import numpy as np
import math
import cconstans
import util
from pygame import Vector2
from pygame.math import clamp
logger = util.Logger(__name__, True)

def get_shoot_pos(goal_pos: np.ndarray, ball_pos: np.ndarray, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    #finding the shooter pos
    ball_to_goal_vec = goal_pos - ball_pos
    shooter_pos: np.ndarray = ball_to_goal_vec * -shooter_offset_scale + goal_pos
    return (shooter_pos[0], shooter_pos[1], math.atan2(*reversed(ball_to_goal_vec)))


class IClient(abc.ABC):
    def __init__(self, client: rsk.Client, team: str = 'blue') -> None:
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.referee: dict = self.client.referee
        self.last_ball_overlap: float = time.time()
        self.goal_pos = np.array([cconstans.goal_pos[0], random.random() * 0.6 - 0.3])
        self.logger = util.Logger(self.__class__.__name__, True)

    def on_pause(self) -> None:
        self.goal_pos = np.array([cconstans.goal_pos[0], random.random() * 0.6 - 0.3])
        self.logger.info(f"running {self.__class__}.on_pause..., goal pos: {round(self.goal_pos[1], 3)}")

    def startup(self) -> None:
        self.logger.info(f"{self.__class__} startup ({str(time.time()).split('.')[1]})")

    def get_shooter_angle(self) -> float:
        return math.degrees(math.atan2(*reversed(self.shooter.position)))

    @abc.abstractmethod
    def update(self) -> None: ...


class MainClient(IClient):
    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        ball = self.client.ball

        if util.is_inside_circle(self.shooter.position, ball, rsk.constants.timed_circle_radius):
            if time.time() - self.last_ball_overlap >= cconstans.timed_circle_timeout:
                self.logger.debug('BOUGE LAAAAAAAAAA')
                pos: Vector2 = Vector2(*(self.shooter.position - ball)).normalize() * rsk.constants.timed_circle_radius + self.shooter.position
                #self.shooter.goto((pos.x, pos.y, self.shooter.orientation), wait=True)
        else:
            self.last_ball_overlap = time.time()

        if 0.1 <= ball[0] < rsk.constants.field_length/2 - rsk.constants.defense_area_length and util.is_inside_court(ball):
            # si la balle est derriere le shooter:
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

            # TODO: check if the shooter is almost aligned with the ball and the goal (be it by angle or by a straight line)
            # sinon si l'angle entre la balle et le robot est trop grand
            elif abs(self.get_shooter_angle()) > 25:
                self.shooter.goto(get_shoot_pos(self.goal_pos, ball, 1.2), wait=True)

            self.shooter.goto(get_shoot_pos(self.goal_pos, ball), wait=False)
            if util.is_inside_circle(self.shooter.position, ball, 0.12):
                self.shooter.kick(1)
                self.logger.debug(f"kicking")
        else:
            self.shooter.goto(self.shooter.pose)



class RotatedClient(IClient):
    def on_pause(self) -> None:
        super().on_pause()
        self.goal_pos = np.array([-cconstans.goal_pos[0], random.random() * 0.6 - 0.3])

    def startup(self) -> None:
        super().startup()
        self.goal_pos = np.array([-cconstans.goal_pos[0], random.random() * 0.6 - 0.3])

    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        ball = self.client.ball

        if util.is_inside_circle(self.shooter.position, ball, rsk.constants.timed_circle_radius):
            if time.time() - self.last_ball_overlap >= cconstans.timed_circle_timeout:
                pos = Vector2(*(self.shooter.position - ball)).normalize() * rsk.constants.timed_circle_radius + self.shooter.position
                #self.shooter.goto((pos.x, pos.y, self.shooter.orientation), wait=True)
        else:
            self.last_ball_overlap = time.time()

        # if the ball is in the right place
        if -0.1 > ball[0] > -rsk.constants.field_length/2 + rsk.constants.defense_area_length and util.is_inside_court(ball):
            # si la balle est derriere le shooter:
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

            # TODO: check if the shooter is almost aligned with the ball and the goal (be it by angle or by a straight line)
            # brouillon:
            # si angle(goal_pos, ball) ~= angle(goal_pos, shooter): ...
            # sinon si l'angle du shooter est trop grand
            elif (180 - abs(self.get_shooter_angle()) > 25) and (not util.is_inside_circle(self.shooter.position, ball, 0.15)):
                self.shooter.goto(get_shoot_pos(self.goal_pos, ball, 1.2), wait=True)
                self.logger.debug("angle too big")

            self.shooter.goto(get_shoot_pos(self.goal_pos, ball), wait=False)
            if util.is_inside_circle(self.shooter.position, ball, 0.12):
                self.shooter.kick(1)
                logger.info(f"kicking")
        else:
            self.shooter.goto(self.shooter.pose)



def main(args: list[str] | None = None):
    arguments = util.get_parser("Script that runs the shooter (adapted to halftime change)").parse_args(sys.argv[1::] if args is None else args)
    logger.info(f"args: {arguments}")
    team: str = arguments.team
    rotated: bool = arguments.rotated

    with rsk.Client(host='rsk.simulateur.les-amicales.fr', key='01234') as c:  # tkt c un bordel mais touche pas ca marche nickel
        shooter_client = MainClient(c, team) if not rotated else RotatedClient(c, team)
        halftime = True
        pause = True
        shooter_client.startup()
        while True:
            if c.referee['halftime_is_running']:
                if halftime:
                    shooter_client = RotatedClient(c, team) if not rotated else MainClient(c, team)
                    logger.info(f"halftime, changing into {shooter_client.__class__}")
                    rotated = not rotated
                    halftime = False
            else:
                halftime = True
            if c.referee["game_paused"]:
                if pause:
                    shooter_client.on_pause()
                    pause = False
            else:
                pause = True

            try:
                shooter_client.update()
            except rsk.client.ClientError as e:
                if not arguments.quiet:
                    shooter_client.logger.warn(e)


if __name__ == "__main__":
    main()
