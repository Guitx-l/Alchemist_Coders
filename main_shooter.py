import abc
import rsk
import time
import math
import util
import random
import numpy as np
from util import angle_of
from pygame import Vector2
from typing import final, Literal, Any, Callable

type array = np.ndarray[2, np.dtype[Any]]

def get_shoot_pos(goal_pos: array, ball_pos: array, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    #finding the shooter pos
    ball_to_goal_vec = goal_pos - ball_pos
    shooter_pos: array = ball_to_goal_vec * -shooter_offset_scale + goal_pos
    return shooter_pos[0], shooter_pos[1], angle_of(ball_to_goal_vec)

def get_alignment(pos1: np.ndarray, pos2: np.ndarray, base: np.ndarray) -> float:
    return abs(angle_of(pos1 - base) - angle_of(pos2 - base))

class BaseShooterClient(util.BaseClient, abc.ABC):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.last_ball_overlap: float = time.time()
        self.goal_pos = np.array([rsk.constants.field_length / 2 * self.goal_sign(), random.random() * 0.6 - 0.3])
        self._last_kick: float = time.time()

    def on_pause(self) -> None:
        self.goal_pos = np.array([rsk.constants.field_length / 2 * self.goal_sign(), random.random() * 0.6 - 0.3])
        self.logger.info(f"running {self.__class__}.on_pause..., goal pos: {np.around(self.goal_pos[1], 3)}")

    def startup(self) -> None:
        self.logger.info(f"{self.__class__} startup ({str(time.time()).split('.')[1]})")

    def is_inside_timed_circle(self) -> bool:
        return util.is_inside_circle(self.shooter.position, self.ball, rsk.constants.timed_circle_radius)

    def kick(self, power: float = 1) -> None:
        if time.time() - self._last_kick > 1:
            self.shooter.kick(power)
            self._last_kick = time.time()

    def ball_behind(self) -> bool:
        """:returns True if the ball is "behind" the shooter else False"""
        if self.goal_sign() == 1:
            return self.ball[0] < self.shooter.position[0]
        return self.ball[0] > self.shooter.position[0]

    def get_opposing_defender(self) -> rsk.client.ClientRobot:
        opposing_team: str = "blue" if self.shooter.team == "green" else "green"
        if self.goal_sign() == 1:
            if self.client.robots[opposing_team][1].position[0] < self.client.robots[opposing_team][2].position[0]:
                return self.client.robots[opposing_team][2]
            return self.client.robots[opposing_team][1]
        else:
            if self.client.robots[opposing_team][1].position[0] > self.client.robots[opposing_team][2].position[0]:
                return self.client.robots[opposing_team][2]
            return self.client.robots[opposing_team][1]

    def goto_condition(self, target: Any, condition: Callable[[], bool] = lambda x: True, raise_exception: bool = False):
        while (not self.shooter.goto(target, wait=False)) and condition():
            self.ball_abuse_evade()
        self.shooter.control(0, 0, 0)
        if raise_exception:
            raise rsk.client.ClientError()

    def abusive_defense_condition(self) -> bool:
        return self.is_inside_defense_zone(self.client.robots[self.shooter.team][2].position) and self.is_inside_defense_zone(self.shooter.position)

    def ball_abuse_evade(self) -> None:
        if self.is_inside_timed_circle():
            if time.time() - self.last_ball_overlap >= 3.0:
                self.logger.debug(f'Avoiding ball_abuse ({round(time.time() - self.last_ball_overlap, 2)})')
                pos = Vector2(*(self.shooter.position - self.ball)).normalize() * rsk.constants.timed_circle_radius + self.shooter.position
                if util.is_inside_court(pos):
                    t = (pos.x, pos.y, self.shooter.orientation)
                else:
                    t = (*Vector2(*(-self.ball)).normalize() * (rsk.constants.timed_circle_radius + 0.1) + self.ball, self.shooter.orientation)
                self.goto_condition(t, self.is_inside_timed_circle)
                self.last_ball_overlap = time.time()
        else:
            self.last_ball_overlap = time.time()

    @final
    def update(self) -> None:
        if self.client.ball is None:
            raise rsk.client.ClientError("#expected: ball is none")
        target = self.shooter.pose

        #evading ball_abuse
        self.ball_abuse_evade()

        # evade abusive_defense
        if self.abusive_defense_condition():
            self.goto_condition((-0.6 * self.goal_sign(), self.shooter.pose[1], self.shooter.pose[2]), condition=self.abusive_defense_condition)
            self.logger.debug("evading abusive defense")
            raise rsk.client.ClientError("#expected: abusive_defense evade")

        elif self.is_inside_defense_zone(self.client.robots[self.shooter.team][2].position) and self.is_inside_defense_zone(self.ball):
            self.logger.debug("evading abusive defense")
            raise rsk.client.ClientError("#expected: abusive_defense evade")

        if util.is_inside_court(self.ball):
            if self.ball_behind():
                ball_vector = Vector2(*(self.shooter.position - self.ball))
                ball_vector.x *= -1
                angle = math.atan2(ball_vector.y * -self.goal_sign(), ball_vector.x * -self.goal_sign())
                if angle >= 0:
                    pos = self.ball + (Vector2(-1, -1).normalize() * 0.25 * self.goal_sign())
                else:
                    pos = self.ball + (Vector2(-1, 1).normalize() * 0.25 * self.goal_sign())
                ball = self.ball
                self.goto_condition((*pos, angle), lambda: Vector2(*(ball - self.ball)).length() < 0.05, raise_exception=True)

            # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
            if math.degrees(get_alignment(self.shooter.position, self.ball, self.goal_pos)) > 10 or (self.is_inside_timed_circle() and not self.faces_ball(self.shooter, 15)):
                target = get_shoot_pos(self.goal_pos, self.ball, 1.2)
            else:
                target = get_shoot_pos(self.goal_pos, self.ball, 0.8)
            if util.is_inside_circle(self.shooter.position, self.ball, 0.12):
                self.kick()

        self.shooter.goto(target, wait=False)



class MainShooterClient(BaseShooterClient):
    def goal_sign(self) -> int:
        return 1



class RotatedShooterClient(BaseShooterClient):
    def goal_sign(self) -> int:
        return -1



if __name__ == "__main__":
    util.start_client(MainShooterClient, RotatedShooterClient)
