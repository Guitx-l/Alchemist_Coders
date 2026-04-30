import rsk
import time
import math
import random
import logging
import numpy as np
from src.util.math import array_type
from src.util.log import getLogger
from src.util.init import start_client
from src.util.math import (
    angle_of, 
    normalized, 
    line_intersects_circle, 
    get_shoot_position, 
    faces_ball, 
    is_inside_circle, 
    is_inside_court, 
    get_angle_between
)
from src.util.bot import get_robot, can_play
# Ritchy Thibault

MISALIGNMENT_ANGLE = math.radians(25)
ALIGNED_SHOOT_OFFSET = 0
MISALIGNED_SHOOT_OFFSET = 0.2

BALL_BEHIND_ANGLE = math.radians(100)
BALL_BEHIND_VECTOR_LENGTH = 0.25
TOP_BALL_BEHIND_VECTORS = {
    -1: normalized([1, 1]) * BALL_BEHIND_VECTOR_LENGTH,
    1: normalized([-1, 1]) * BALL_BEHIND_VECTOR_LENGTH
}
BOTTOM_BALL_BEHIND_VECTORS = {
    -1: normalized([1, -1]) * BALL_BEHIND_VECTOR_LENGTH,
    1: normalized([-1, -1]) * BALL_BEHIND_VECTOR_LENGTH
}

BALL_ABUSE_THRESHOLD = 2.5

KICK_CIRCLE_RADIUS = 0.13
KICK_TIME_THRESHOLD = 1.0

SHOOT_POSITIONS_SWEEP_NUMBER = 10
SHOOT_POSITIONS = {
    -1: np.array([0.92, 0.0]),
    1: np.array([-0.92, 0.0])
}


def get_shooter_dict() -> dict:
    return {
        "last_kick": time.time(),
        "goal_pos": np.array([0.0, 0.0]),
        "logger": getLogger("shooter"),
        "last_ball_overlap": time.time(),
    }


def is_inside_timed_circle(shooter: rsk.client.ClientRobot, ball: array_type) -> bool:
    return is_inside_circle(shooter.position, ball, rsk.constants.timed_circle_radius)


def evade_ball_abuse(shooter: rsk.client.ClientRobot, ball: array_type, data: dict) -> bool:    
    if is_inside_timed_circle(shooter, ball):
        if time.time() - data['last_ball_overlap'] > BALL_ABUSE_THRESHOLD:
            evade_target = normalized(shooter.position - ball) * rsk.constants.timed_circle_radius + shooter.position
            if not is_inside_court(evade_target):
                evade_target = normalized(-ball) * rsk.constants.timed_circle_radius + ball
            shooter.goto((evade_target[0], evade_target[1], shooter.orientation), wait=False)
            return True
    else:
        data['last_ball_overlap'] = time.time()
    return False


def get_goal_position(client: rsk.Client, ball: array_type, team: str, data: dict) -> array_type:
        i = 0
        opp_robot_1 = get_robot(client, "green" if team == "blue" else "blue", 1)
        opp_robot_2 = get_robot(client, "green" if team == "blue" else "blue", 2)
        new_goal_pos = data["goal_pos"].copy()
        modified = False
      
        while (
            (line_intersects_circle(ball, new_goal_pos, opp_robot_1.position, 0.1) or line_intersects_circle(ball, new_goal_pos, opp_robot_2.position, 0.1)) 
            and i < 10
        ):
            i += 1
            new_goal_pos[1] = random.random() * 0.6 - 0.3
            modified = True

        if i >= 10:
            modified = False
        if modified:
            # data["logger"].debug(f"Goal position reset: Could find a trajectory after {i} attempts ({round(data['goal_pos'][1], 3)} -> {round(new_goal_pos[1], 3)})")
            data["goal_pos"] = new_goal_pos
        return data["goal_pos"]


def shooter_update(client: rsk.Client, team: str, number: int, goal_sign: int, ball: array_type, data: dict) -> None: # average fps = 90
    logger: logging.Logger = data["logger"]
    shooter: rsk.client.ClientRobot = get_robot(client, team, number)
    goal_pos: array_type = data["goal_pos"]

    if client.referee['game_paused']:
        data['last_ball_overlap'] = time.time()

    if evade_ball_abuse(shooter, ball, data) or not can_play(shooter, client.referee):
        return

    goal_pos[0] = 0.92 * goal_sign
    target = shooter.pose.copy()

    if not is_inside_court(ball):
        shooter.goto(shooter.pose, wait=False)
        return

    # if the shooter is behind the ball, then go to the side
    ball_vector = shooter.position - ball
    ball_vector[0] = ball_vector[0] * goal_sign
    if abs(angle_of(ball_vector)) < BALL_BEHIND_ANGLE:
        logger.debug("Ball behind detected, evading to the side...")
        if shooter.pose[1] > ball[1]:
            ball_behind_target = ball + TOP_BALL_BEHIND_VECTORS[goal_sign]
        else:
            ball_behind_target = ball + BOTTOM_BALL_BEHIND_VECTORS[goal_sign]
        target = (ball_behind_target[0], ball_behind_target[1], angle_of(ball - ball_behind_target))

    # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
    elif (
        get_angle_between(shooter.position - goal_pos, ball - goal_pos) > MISALIGNMENT_ANGLE
        or (is_inside_timed_circle(shooter, ball) and not faces_ball(shooter, ball))
    ):
        goal_pos = get_goal_position(client, ball, team, data)
        target = get_shoot_position(goal_pos, ball, MISALIGNED_SHOOT_OFFSET)
    else:
        goal_pos = get_goal_position(client, ball, team, data)
        target = get_shoot_position(goal_pos, ball, ALIGNED_SHOOT_OFFSET)

    
    if (
        is_inside_circle(shooter.position, ball, KICK_CIRCLE_RADIUS) 
        and faces_ball(shooter, ball) 
        and time.time() - data["last_kick"] > KICK_TIME_THRESHOLD
    ):
        logger.debug("Kicking...")
        shooter.kick(1)
        data["last_kick"] = time.time()
    else:
        shooter.goto(target, wait=False)


if __name__ == "__main__":
    start_client(shooter_update, number=1, data_dict=get_shooter_dict())
