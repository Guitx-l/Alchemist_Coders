import enum
import time
import rsk
import math
import numpy as np
import src.util.math as math_util
from src.util.log import getLogger
from src.util import array_type
from src.bot import can_play, get_goal_sign, get_ball, get_robot
from src.util.init import start_client


class Strategy(enum.Enum):
    NONE = enum.auto()
    BALL_RUSH = enum.auto()
    TAN_SHOOTER = enum.auto()
    THALES_SHOOTER = enum.auto()
    BALL_VECTOR = enum.auto()
    BALL_BEHIND = enum.auto()
    PROJECT = enum.auto()


def get_keeper_dict() -> dict:
    return {
        "last_ball_position": np.zeros(2),
        "last_timestamp": time.time(),
        "logger": getLogger("goalkeeper"),
    }


def is_inside_defense_zone(point: array_type, goal_sign: int) -> bool:
    if goal_sign == 1:
        return math_util.is_inside_left_zone(point)
    return math_util.is_inside_right_zone(point)


def get_opposing_shooter(client: rsk.Client, team: str, ball: array_type) -> rsk.client.ClientRobot:
        opposing_team = "blue" if team == "green" else "green"
        opp_1 = get_robot(client, opposing_team, 1)
        opp_2 = get_robot(client, opposing_team, 2)

        if np.linalg.norm(opp_1.position - ball) < np.linalg.norm(opp_2.position - ball):
            return opp_1
        return opp_2


def goalkeeper_update(client: rsk.Client, team: str, number: int, data: dict) -> None:
    keeper = get_robot(client, team, number)
    goal_sign = get_goal_sign(client, team)
    strategy = Strategy.NONE
    ball = get_ball(client)
    last_ball_position = data['last_ball_position']
    target_x = -0.92 * goal_sign
    target_y = keeper.position[1]
    
    if not math_util.is_inside_court(ball):
        keeper.goto(keeper.pose)
        return

    opp_shooter = get_opposing_shooter(client, team, ball)
    team_mate = get_robot(client, team, 3 - number) # 3 - 1 = 2 and 3 - 2 = 1
    goal_post_x = -0.92 * goal_sign
    no_shooter = np.linalg.norm(ball - opp_shooter.position) > 0.18

    if no_shooter and (np.linalg.norm(ball - last_ball_position) > 0.05):
        ball_vector = ball - last_ball_position
        target_y = ball[1] + (ball_vector[1] * (goal_post_x - last_ball_position[0]) / ball_vector[0])
        strategy = Strategy.BALL_VECTOR
        
    elif (
        no_shooter
        and (ball[0] * goal_sign < 0.2)
        # if the teammate is close to the ball
        and not (not np.linalg.norm(ball - team_mate.position) > 0.3 and can_play(team_mate, client.referee)) 
    ):
        target_x, target_y = ball
        strategy = Strategy.BALL_RUSH

    elif math_util.faces_ball(opp_shooter, ball, 20):
        target_y = opp_shooter.pose[1] + (math.tan(opp_shooter.pose[2]) * (goal_post_x - opp_shooter.pose[0]))
        strategy = Strategy.TAN_SHOOTER

    elif math_util.get_misalignment(np.array([target_x, target_y]), ball, opp_shooter.position) < 10:
        target_y = ball[1] + (ball[1] - opp_shooter.pose[1]) / (ball[0] - opp_shooter.pose[0]) * (goal_post_x - ball[0])
        strategy = Strategy.THALES_SHOOTER


    if (
        not is_inside_defense_zone(ball, goal_sign) 
        and ball[0] * goal_sign < 0.1 
        and strategy not in (Strategy.NONE, Strategy.BALL_RUSH)
    ):
        target_x, target_y = math_util.project_on_line(keeper.position, np.array([target_x, target_y]), ball)
        strategy = Strategy.PROJECT
    elif strategy != Strategy.BALL_RUSH:
        target_y = np.clip(target_y, -0.25, 0.25)

    ball_vector = keeper.position - ball
    ball_vector[0] = ball_vector[0] * goal_sign
    if abs(math_util.angle_of(ball_vector)) < math.radians(100):
        if keeper.pose[1] > ball[1]:
            target_x, target_y = ball + (math_util.normalized([-1 * goal_sign, 1]) * 0.25)
        else:
            target_x, target_y = ball + (math_util.normalized([-1 * goal_sign, -1]) * 0.25)
        strategy = Strategy.BALL_BEHIND

    # TODO: Avoid collisions with teammates when near to target

    keeper.goto((target_x, target_y, math.pi if goal_sign == -1 else 0), wait=False)

    if math_util.is_inside_circle(ball, keeper.position, 0.15):
        keeper.kick(1)

    if time.time() - data['last_timestamp'] > 0.2:
        data["last_ball_position"] = ball.copy()
        data["last_timestamp"] = time.time()


if __name__ == "__main__":
    start_client(goalkeeper_update, number=1, data_dict=get_keeper_dict())
