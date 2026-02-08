"""
La ou ya tous les bots
"""
import rsk
from typing import Sequence
from src.util.math import is_inside_left_zone, is_inside_right_zone
from src.util import array_type


def can_play(bot: rsk.client.ClientRobot, referee: dict) -> bool:
    return (not referee['teams'][bot.team]['robots'][str(bot.number)]['preempted']) and (not referee['teams'][bot.team]['robots'][str(bot.number)]['penalized'])


def get_goal_sign(client: rsk.Client, team: str) -> int:
    return -1 if client.referee['teams'][team]['x_positive'] else 1


def get_ball(client: rsk.Client) -> array_type:
    if client.ball is None:
        raise rsk.client.ClientError("#ball is none")
    return client.ball.copy()


def is_inside_defense_zone(goal_sign: int, pos: Sequence[float]) -> bool:
    if goal_sign == 1:
        return is_inside_left_zone(pos)
    return is_inside_right_zone(pos)


def get_robot(client: rsk.Client, team: str, number: int) -> rsk.client.ClientRobot:
    robot = client.robots[team][number]
    if not robot.has_position(skip_old=True):
        raise rsk.client.ClientError(f"#Impossible de trouver le robot {team}{number}.")
    return robot

