import abc
import rsk
import time
import math
import util
import random
import numpy as np
from util import angle_of, normalized, line_intersects_circle, get_alignment, get_shoot_position
from typing import Literal, Any, Callable

type array = np.ndarray[np.dtype[np.floating]]



class BaseShooterClient(util.BaseClient, abc.ABC):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.last_ball_overlap: float = time.time()
        self._goal_pos: array = np.array([rsk.constants.field_length / 2 * self.goal_sign(), random.random() * 0.6 - 0.3])
        self._last_kick: float = time.time()

    def on_pause(self) -> None:
        self._goal_pos = np.array([rsk.constants.field_length / 2 * self.goal_sign(), random.random() * 0.6 - 0.3])
        self.logger.info(f"running {self.__class__}.on_pause..., goal pos: {np.around(self.get_goal_position()[1], 3)}")

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

    def goto_condition(self, target: Any, condition: Callable[[], bool] = lambda: True, raise_exception: bool = False):
        # regarde le code du goto originel
        while (not self.shooter.goto(target, wait=False)) and condition():
            self.ball_abuse_evade()
        self.shooter.control(0, 0, 0)
        if raise_exception:
            raise rsk.client.ClientError("#goto_condition reset")

    def ball_abuse_evade(self) -> bool:
        if self.is_inside_timed_circle():
            if time.time() - self.last_ball_overlap > 2.5:
                #self.logger.debug(f'Avoiding ball_abuse ({round(time.time() - self.last_ball_overlap, 2)})')
                pos = normalized(self.shooter.position - self.ball) * rsk.constants.timed_circle_radius + self.shooter.position
                if util.is_inside_court(pos):
                    t = (pos[0], pos[1], self.shooter.orientation)
                else:
                    t = (*normalized(-self.ball) * (rsk.constants.timed_circle_radius + 0.05) + self.ball, self.shooter.orientation)
                self.shooter.goto(t, wait=False)
                return True
        else:
            self.last_ball_overlap = time.time()
        return False

    def get_goal_position(self) -> array:
        i = 0
        opp_robot_1 = self.client.robots["green" if self.shooter.team == "blue" else "blue"][1]
        opp_robot_2 = self.client.robots["green" if self.shooter.team == "blue" else "blue"][2]
        new_goal_pos = self._goal_pos.copy()
        modified = False

        while (line_intersects_circle(self.ball, new_goal_pos, opp_robot_1.position, 0.09) or line_intersects_circle(self.ball, new_goal_pos, opp_robot_2.position, 0.09)) and i < 20:
            i += 1
            new_goal_pos[1] = random.random() * 0.6 - 0.3
            modified = True

        if i >= 20:
            modified = False
        if modified:
            self.logger.debug(f"Goal position reset: Could find a trajectory after {i} attempts ({round(self._goal_pos[1], 3)} -> {round(new_goal_pos[1], 3)})")
            self._goal_pos[1] = new_goal_pos[1]
        return self._goal_pos

    def update(self) -> None:
        target = self.shooter.pose

        if not util.is_inside_court(self.ball):
            self.shooter.goto(self.shooter.pose, wait=False)
            return

        # if evading ball_abuse
        if self.ball_abuse_evade():
            return

        if self.ball_behind():
            ball_vector = self.shooter.position - self.ball
            ball_vector[0] *= -1
            if angle_of(ball_vector * -self.goal_sign()) >= 0:
                pos = self.ball + (normalized([-1, -1]) * 0.25 * self.goal_sign())
            else:
                pos = self.ball + (normalized([-1, 1]) * 0.25 * self.goal_sign())
            ball = self.ball.copy()
            self.goto_condition((*pos, angle_of(self.ball - pos)), condition=lambda: np.linalg.norm(self.ball - ball) < 0.05, raise_exception=True)

        # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
        if math.degrees(get_alignment(self.shooter.position, self.ball, self.get_goal_position())) > 10 or (self.is_inside_timed_circle() and not self.faces_ball(self.shooter, 15)):
            target = get_shoot_position(self.get_goal_position(), self.ball, 1.2)
        else:
            target = get_shoot_position(self.get_goal_position(), self.ball, 0.8)
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
