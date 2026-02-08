import rsk
import time
import math
import random
import logging
import numpy as np
from src.util.log import getLogger
from src.util.math import angle_of, normalized, line_intersects_circle, get_misalignment, get_shoot_position, faces_ball, array_type, is_inside_circle, is_inside_court
from src.bot import get_ball, get_goal_sign
from src.util.init import start_client


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
        if time.time() - data['last_ball_overlap'] > 2.5:
            pos = normalized(shooter.position - ball) * rsk.constants.timed_circle_radius + shooter.position
            if is_inside_court(pos):
                t = (pos[0], pos[1], shooter.orientation)
            else:
                t = (*(normalized(-ball) * 0.3 + ball), shooter.orientation)
            shooter.goto(t, wait=False)
            return True
    else:
        data['last_ball_overlap'] = time.time()
    return False


def get_goal_position(client: rsk.Client, ball: array_type, team: str, data: dict) -> array_type:
        i = 0
        opp_robot_1 = client.robots["green" if team == "blue" else "blue"][1]
        opp_robot_2 = client.robots["green" if team == "blue" else "blue"][2]
        new_goal_pos = data["goal_pos"].copy()
        modified = False

        while (
            (line_intersects_circle(ball, new_goal_pos, opp_robot_1.position, 0.1) or line_intersects_circle(ball, new_goal_pos, opp_robot_2.position, 0.1)) 
            and i < 20
        ):
            i += 1
            new_goal_pos[1] = random.random() * 0.6 - 0.3
            modified = True

        if i >= 20:
            modified = False
        if modified:
            data["logger"].debug(f"Goal position reset: Could find a trajectory after {i} attempts ({round(data['goal_pos'][1], 3)} -> {round(new_goal_pos[1], 3)})")
            data["goal_pos"] = new_goal_pos
        return data["goal_pos"]


def shooter_update(client: rsk.Client, team: str, number: int, data: dict) -> None: # average fps = 90
    logger: logging.Logger = data["logger"]
    shooter: rsk.client.ClientRobot = client.robots[team][number]
    ball: array_type = get_ball(client)
    goal_sign: int = get_goal_sign(client, team)
    goal_pos: array_type = data["goal_pos"]

    if evade_ball_abuse(shooter, ball, data):
        return

    goal_pos[0] = 0.92 * goal_sign
    target = shooter.pose.copy()
    
    if client.referee['game_paused']:
        data['last_ball_overlap'] = time.time()

    if not is_inside_court(ball):
        shooter.goto(shooter.pose, wait=False)
        return

    # if the shooter is behind the ball, then go to the side
    ball_vector = shooter.position - ball
    ball_vector[0] = ball_vector[0] * goal_sign
    if abs(angle_of(ball_vector)) < math.radians(100):
        if shooter.pose[1] > ball[1]:
            pos = ball + (normalized([-1 * goal_sign, 1]) * 0.25)
        else:
            pos = ball + (normalized([-1 * goal_sign, -1]) * 0.25)
        target = (pos[0], pos[1], angle_of(ball - pos))

    # else if the ball, the shooter and the goal and kind of misaligned or the shooter is inside the timed circle
    elif (
        get_misalignment(shooter.position, ball, goal_pos) > math.radians(25) 
        or (is_inside_timed_circle(shooter, ball) and not faces_ball(shooter, ball, 15))
    ):
        goal_pos = get_goal_position(client, ball, team, data)
        target = get_shoot_position(goal_pos, ball, 0.2)
        logger.debug("Repositioning...")
    else:
        goal_pos = get_goal_position(client, ball, team, data)
        target = get_shoot_position(goal_pos, ball, -0.2)
        logger.debug("Going straight at ball...")

    shooter.goto(target, wait=False)
    if is_inside_circle(shooter.position, ball, 0.13) and faces_ball(shooter, ball, 15):
        if time.time() - data["last_kick"] > 1:
            logger.debug("Kicking...")
            shooter.kick(1)
            data["last_kick"] = time.time()


if __name__ == "__main__":
    start_client(shooter_update, number=1, data_dict=get_shooter_dict())
