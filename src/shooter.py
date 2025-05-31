import abc
import rsk
import time
import math
import util
import random
import numpy as np
from util import angle_of, normalized, line_intersects_circle, get_alignment, get_shoot_position
from typing import Literal

type array = np.ndarray[np.dtype[np.floating]]



class ShooterClient(util.BaseClient):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.shooter: rsk.client.ClientRobot = client.robots[team][1]
        self.last_ball_overlap: float = time.time()
        self._goal_pos: array = np.array([rsk.constants.field_length / 2 * self.goal_sign(), random.random() * 0.6 - 0.3])

    def is_inside_timed_circle(self) -> bool:
        return util.is_inside_circle(self.shooter.position, self.ball, rsk.constants.timed_circle_radius)

    def evade_ball_abuse(self) -> bool:
        if self.is_inside_timed_circle():
            if time.time() - self.last_ball_overlap > 2.5:
                pos = normalized(self.shooter.position - self.ball) * rsk.constants.timed_circle_radius + self.shooter.position
                if util.is_inside_court(pos):
                    t = (pos[0], pos[1], self.shooter.orientation)
                else:
                    t = (*(normalized(-self.ball) * 0.3 + self.ball), self.shooter.orientation)
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
            self._goal_pos = new_goal_pos
        return self._goal_pos

    def update(self) -> None:
        target = self.shooter.pose
        self._goal_pos[0] = 0.92 * self.goal_sign()
        if not util.is_inside_court(self.ball):
            self.shooter.goto(self.shooter.pose, wait=False)
            return

        # if evading ball_abuse
        if self.evade_ball_abuse():
            return

        ball_vector = self.shooter.position - self.ball
        ball_vector[0] = ball_vector[0] * self.goal_sign()
        if abs(util.angle_of(ball_vector)) < math.radians(100):
            if self.shooter.pose[1] > self.ball[1]:
                pos = self.ball + (util.normalized([-1 * self.goal_sign(), 1]) * 0.25)
            else:
                pos = self.ball + (util.normalized([-1 * self.goal_sign(), -1]) * 0.25)
            target = (*pos, angle_of(self.ball - pos))

        # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
        elif math.degrees(get_alignment(self.shooter.position, self.ball, self.get_goal_position())) > 10 or (self.is_inside_timed_circle() and not self.faces_ball(self.shooter, 15)):
            target = get_shoot_position(self.get_goal_position(), self.ball, 1.2)
        else:
            target = get_shoot_position(self.get_goal_position(), self.ball, 0.8)
        if util.is_inside_circle(self.shooter.position, self.ball, 0.15):
            self.shooter.kick(1)

        self.shooter.goto(target, wait=False)



if __name__ == "__main__":
    util.start_client(ShooterClient)
