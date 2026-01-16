import rsk
import time
import math
import random
import numpy as np
import dataclasses
from src.util.math import angle_of, normalized, line_intersects_circle, get_alignment, get_shoot_position, faces_ball, array_type, is_inside_circle, is_inside_court
from src.bot import BotData
from src.util.init import start_client
from typing import Literal


def evade_ball_abuse(data: ShooterData) -> bool:
    if data.is_inside_timed_circle():
        if time.time() - data.last_ball_overlap > 2.5:
            pos = normalized(data.shooter.position - data.ball) * rsk.constants.timed_circle_radius + data.shooter.position
            if is_inside_court(pos):
                t = (pos[0], pos[1], data.shooter.orientation)
            else:
                t = (*(normalized(-data.ball) * 0.3 + data.ball), data.shooter.orientation)
            data.shooter.goto(t, wait=False)
            return True
    else:
        data.last_ball_overlap = time.time()
    return False


def get_goal_position(data: ShooterData) -> array_type:
        i = 0
        opp_robot_1 = data.client.robots["green" if data.team == "blue" else "blue"][1]
        opp_robot_2 = data.client.robots["green" if data.team == "blue" else "blue"][2]
        new_goal_pos = data._goal_pos.copy()
        modified = False

        while (line_intersects_circle(data.ball, new_goal_pos, opp_robot_1.position, 0.09) or line_intersects_circle(data.ball, new_goal_pos, opp_robot_2.position, 0.09)) and i < 20:
            i += 1
            new_goal_pos[1] = random.random() * 0.6 - 0.3
            modified = True

        if i >= 20:
            modified = False
        if modified:
            data.logger.debug(f"Goal position reset: Could find a trajectory after {i} attempts ({round(data._goal_pos[1], 3)} -> {round(new_goal_pos[1], 3)})")
            data._goal_pos = new_goal_pos
        return data._goal_pos


@dataclasses.dataclass
class ShooterData(BotData):
    last_ball_overlap: float = dataclasses.field(default_factory=time.time)
    last_kick: float = dataclasses.field(default_factory=time.time)
    shooter: rsk.client.ClientRobot = dataclasses.field(init=False)
    _goal_pos: array_type = dataclasses.field(default_factory=lambda: np.array([rsk.constants.field_length / 2, random.random() * 0.6 - 0.3]))

    def __post_init__(self):
        super().__post_init__()
        self.shooter = self.client.robots[self.team][0]

    def is_inside_timed_circle(self) -> bool:
        return is_inside_circle(self.shooter.position, self.ball, rsk.constants.timed_circle_radius)


def update(data: ShooterData) -> None:
    target = data.shooter.pose
    data._goal_pos[0] = 0.92 * data.goal_sign()

    if data.client.referee['game_paused']:
        data.last_ball_overlap = time.time()

    if not is_inside_court(data.ball):
        data.shooter.goto(data.shooter.pose, wait=False)
        return

    # if evading ball_abuse
    if evade_ball_abuse(data):
        return

    ball_vector = data.shooter.position - data.ball
    ball_vector[0] = ball_vector[0] * data.goal_sign()
    if abs(angle_of(ball_vector)) < math.radians(100):
        if data.shooter.pose[1] > data.ball[1]:
            pos = data.ball + (normalized([-1 * data.goal_sign(), 1]) * 0.25)
        else:
            pos = data.ball + (normalized([-1 * data.goal_sign(), -1]) * 0.25)
        target = (*pos, angle_of(data.ball - pos))

    # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
    elif math.degrees(get_alignment(data.shooter.position, data.ball, get_goal_position(data))) > 25 or (data.is_inside_timed_circle() and not faces_ball(data.shooter, data.ball, 15)):
        target = get_shoot_position(get_goal_position(data), data.ball, 1.2)
    else:
        target = get_shoot_position(get_goal_position(data), data.ball, 0.8)

    data.shooter.goto(target, wait=False)
    if is_inside_circle(data.shooter.position, data.ball, 0.13):
        if time.time() - data.last_kick > 1:
            data.shooter.kick(1)
            data.last_kick = time.time()


if __name__ == "__main__":
    start_client(ShooterData, update)
