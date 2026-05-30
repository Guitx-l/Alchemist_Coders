import rsk
import time
import math
import random
import logging
import numpy as np
from src.util.math import array_type
from src.util.log import get_logger
from src.util.init import start_client
from src.util.math import (
    angle_of, 
    normalized, 
    line_intersects_circle, 
    get_shoot_position, 
    faces_object, 
    is_inside_circle, 
    is_inside_court, 
    distance_to_line
)
from src.bot.ball_anticipation import get_dynamic_future_ball
from src.util.bot import get_robot, can_play
# Ritchy Thibault

MISALIGNMENT_ANGLE = math.radians(25)
ALIGNED_SHOOT_OFFSET = -0.2
MISALIGNED_SHOOT_OFFSET = 0.18

BALL_BEHIND_ANGLE = math.radians(100)
BALL_BEHIND_VECTOR_LENGTH = 0.23
TOP_BALL_BEHIND_VECTORS = {
    -1: normalized([1, 1]) * BALL_BEHIND_VECTOR_LENGTH,
    1: normalized([-1, 1]) * BALL_BEHIND_VECTOR_LENGTH
}
BOTTOM_BALL_BEHIND_VECTORS = {
    -1: normalized([1, -1]) * BALL_BEHIND_VECTOR_LENGTH,
    1: normalized([-1, -1]) * BALL_BEHIND_VECTOR_LENGTH
}

BALL_ABUSE_THRESHOLD = 2.5

KICK_CIRCLE_RADIUS = 0.14
KICK_TIME_THRESHOLD = 1.0

SHOOT_POSITIONS_SWEEP_NUMBER = 5
SHOOT_POSITIONS = {
    -1: [np.array([-0.92, y]) for y in np.linspace(-0.25, 0.25, SHOOT_POSITIONS_SWEEP_NUMBER)],
    1: [np.array([0.92, y]) for y in np.linspace(-0.25, 0.25, SHOOT_POSITIONS_SWEEP_NUMBER)]
}


def get_shooter_dict() -> dict:
    return {
        "last_kick": time.time(),
        "goal_pos": np.array([0.0, 0.0]),
        "logger": get_logger("shooter"),
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


def is_good_trajectory(ball: array_type, goal_pos: array_type, defenders: list[rsk.client.ClientRobot]):
    return all(not line_intersects_circle(ball, goal_pos, robot.position, rsk.constants.robot_radius, segment=True) for robot in defenders)

def get_goal_position(client: rsk.Client, shooter: rsk.client.ClientRobot, ball: array_type, team: str, data: dict, goal_sign: int) -> array_type:
    opp_robot_1 = get_robot(client, "green" if team == "blue" else "blue", 1)
    opp_robot_2 = get_robot(client, "green" if team == "blue" else "blue", 2)
    old_goal_pos: array_type = data["goal_pos"]
    optimal_position = np.array([0.92 * goal_sign, shooter.pose[1] + (math.tan(shooter.pose[2]) * (0.92 * goal_sign - shooter.pose[0]))])
    optimal_position[1] = np.clip(optimal_position[1], -0.25, 0.25)
    new_goal_pos = optimal_position
    
    defenders = [
        i for i in [opp_robot_1, opp_robot_2] 
        if can_play(i, client.referee) 
        if i.position[0] * goal_sign > ball[0] * goal_sign
    ]

    if is_good_trajectory(ball, old_goal_pos, defenders):
        return old_goal_pos

    possible_goal_pos = [pos for pos in SHOOT_POSITIONS[goal_sign] if is_good_trajectory(ball, pos, defenders)]

    if len(defenders) == 0 or is_good_trajectory(ball, optimal_position, defenders) or len(possible_goal_pos) == 0:
        data["goal_pos"] = optimal_position
        return optimal_position
    
    def goal_position_key(goal_position: np.ndarray) -> float:
        closest_defender = min(defenders, key=lambda robot: distance_to_line(robot.position, goal_position, ball, segment=True))
        return distance_to_line(closest_defender.position, goal_position, ball, segment=True)

    new_goal_pos = max(possible_goal_pos, key=goal_position_key)
    data["goal_pos"] = new_goal_pos
    return new_goal_pos 



def shooter_update(client: rsk.Client, team: str, number: int, goal_sign: int, ball: array_type, data: dict) -> None: # average fps = 90
    logger: logging.Logger = data["logger"]
    if client.referee['game_paused']:
        data['last_ball_overlap'] = time.time()

    is_kicking = False
    future_ball = get_dynamic_future_ball(client)
    if future_ball is None:
        future_ball = ball
    shooter: rsk.client.ClientRobot = get_robot(client, team, number)
    goal_pos = get_goal_position(client, shooter, future_ball, team, data, goal_sign)


    if client.referee['game_paused']:
        data['last_ball_overlap'] = time.time()

    if evade_ball_abuse(shooter, ball, data) or not can_play(shooter, client.referee):
        return

    target = shooter.pose.copy()

    if not is_inside_court(ball):
        shooter.goto(shooter.pose, wait=False)
        return

    # if the shooter is behind the ball, then go to the side
    ball_vector = shooter.position - ball
    ball_vector[0] = ball_vector[0] * goal_sign
    if abs(angle_of(ball_vector)) < BALL_BEHIND_ANGLE:
        if shooter.pose[1] > ball[1]:
            ball_behind_target = future_ball + TOP_BALL_BEHIND_VECTORS[goal_sign]
        else:
            ball_behind_target = future_ball + BOTTOM_BALL_BEHIND_VECTORS[goal_sign]
        target = (ball_behind_target[0], ball_behind_target[1], angle_of(future_ball - ball_behind_target))

    # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
    elif (
        is_inside_timed_circle(shooter, ball) 
        and faces_object(shooter, ball) and faces_object(shooter, goal_pos)
    ):
        target = get_shoot_position(goal_pos, future_ball, ALIGNED_SHOOT_OFFSET)
        if np.linalg.norm(shooter.position - ball) < KICK_CIRCLE_RADIUS:
            logger.debug("Kicking...")
            shooter.kick(1)
            data["last_kick"] = time.time()
            is_kicking = True
    else:
        target = get_shoot_position(goal_pos, future_ball, MISALIGNED_SHOOT_OFFSET)

    if not is_kicking:
        shooter.goto(target, wait=False)


if __name__ == "__main__":
    start_client(shooter_update, number=1, data_dict=get_shooter_dict())
