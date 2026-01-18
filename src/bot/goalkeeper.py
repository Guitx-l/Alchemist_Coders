import enum
import time
import rsk
import math
import numpy as np
from typing import Literal
import src.util.math as math_util
from src.util import array_type
from src.bot import BotData
from src.util.init import start_client


class Strategy(enum.Enum):
    NONE = enum.auto()
    BALL_RUSH = enum.auto()
    TAN_SHOOTER = enum.auto()
    THALES_SHOOTER = enum.auto()
    BALL_VECTOR = enum.auto()
    BALL_BEHIND = enum.auto()
    PROJECT = enum.auto()


class GoalKeeperData(BotData):
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue']) -> None:
        super().__init__(client, team)
        self.keeper: rsk.client.ClientRobot = self.client.robots[self.team][2]
        self.last_ball_position = np.zeros(2)
        self.strategy = Strategy.NONE
        self.last_timestamp = time.time()


def get_opposing_shooter(bot_data: GoalKeeperData) -> rsk.client.ClientRobot:
        opposing_team: str = "blue" if bot_data.keeper.team == "green" else "green"
        opp_1 = bot_data.client.robots[opposing_team][1]
        opp_2 = bot_data.client.robots[opposing_team][2]

        if np.linalg.norm(opp_1.position - bot_data.ball) < np.linalg.norm(opp_2.position - bot_data.ball):
            return opp_1
        return opp_2


def update(data: GoalKeeperData) -> None:
    target_x = -0.92 * data.goal_sign()
    target_y = data.keeper.position[1]
    data.strategy = Strategy.NONE

    if not math_util.is_inside_court(data.ball):
        data.keeper.goto(data.keeper.pose)
        return

    opp_shooter = get_opposing_shooter(data).pose
    team_mate = data.client.robots[data.team][3 - data.keeper.number].position
    goal_post_x = -0.92 * data.goal_sign()
    no_shooter = np.linalg.norm(data.ball - opp_shooter[:2]) > 0.18

    if no_shooter and (np.linalg.norm(data.ball - data.last_ball_position) > 0.05):
        ball_vector = data.ball - data.last_ball_position
        target_y = data.ball[1] + (ball_vector[1] * (goal_post_x - data.last_ball_position[0]) / ball_vector[0])
        data.strategy = Strategy.BALL_VECTOR
        
    elif no_shooter and (data.ball[0] * data.goal_sign() < 0.2) and (np.linalg.norm(data.ball - team_mate) > 0.3):
        target_x, target_y = data.ball
        data.strategy = Strategy.BALL_RUSH

    elif math_util.faces_ball(get_opposing_shooter(data), data.ball, 20):
        target_y = opp_shooter[1] + (math.tan(opp_shooter[2]) * (goal_post_x - opp_shooter[0]))
        data.strategy = Strategy.TAN_SHOOTER

    elif math_util.get_alignment(np.array([target_x, target_y]), data.ball, opp_shooter[:2]) < 10:
        target_y = data.ball[1] + (data.ball[1] - opp_shooter[1]) / (data.ball[0] - opp_shooter[0]) * (goal_post_x - data.ball[0])
        data.strategy = Strategy.THALES_SHOOTER


    if not data.is_inside_defense_zone(data.ball) and data.ball[0] * data.goal_sign() < 0.1 and data.strategy not in (Strategy.NONE, Strategy.BALL_RUSH):
        goal_pos = np.array([target_x, target_y])
        trajectory = data.ball - goal_pos
        new_target = goal_pos + trajectory * (np.dot(data.keeper.position - goal_pos, trajectory) / np.linalg.norm(trajectory) ** 2)
        target_x, target_y = new_target
        data.strategy = Strategy.PROJECT
    elif data.strategy != Strategy.BALL_RUSH:
        target_y = np.clip(target_y, -0.25, 0.25)

    ball_vector = data.keeper.position - data.ball
    ball_vector[0] = ball_vector[0] * data.goal_sign()
    if abs(math_util.angle_of(ball_vector)) < math.radians(100):
        if data.keeper.pose[1] > data.ball[1]:
            target_x, target_y = data.ball + (math_util.normalized([-1 * data.goal_sign(), 1]) * 0.25)
        else:
            target_x, target_y = data.ball + (math_util.normalized([-1 * data.goal_sign(), -1]) * 0.25)
        data.strategy = Strategy.BALL_BEHIND

    data.keeper.goto((target_x, target_y, math.pi if data.goal_sign() == -1 else 0), wait=False)

    if math_util.is_inside_circle(data.ball, data.keeper.position, 0.15):
        data.keeper.kick(1)

    if time.time() - data.last_timestamp > 0.2:
        data.last_ball_position = data.ball.copy()
        data.last_timestamp = time.time()



if __name__ == "__main__":
    start_client(GoalKeeperData, update)
