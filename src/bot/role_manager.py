import rsk
from src.util import array_type
from src.util.log import getLogger
from src.bot import can_play, get_robot
from src.bot.shooter import shooter_update, get_shooter_dict
from src.bot.goalkeeper import goalkeeper_update, get_keeper_dict

FLICKER_DISTANCE_THRESHOLD = 0.05
ATTACK_MODE_THRESHOLD = 0

def is_shooter(client: rsk.Client, team: str, number: int, goal_sign: int, ball) -> bool:
    bot = get_robot(client, team, number)
    other_bot = get_robot(client, team, 3 - number)

    if not can_play(other_bot, client.referee):
        return ball[0] * goal_sign > ATTACK_MODE_THRESHOLD
    
    if abs(bot.position[0] - other_bot.position[0]) < FLICKER_DISTANCE_THRESHOLD:
        return bot.number == 1
    
    return bot.position[0] * goal_sign > other_bot.position[0] * goal_sign


def get_role_manager_dict() -> dict:
    return {
        "shooter_data": get_shooter_dict(),
        "keeper_data": get_keeper_dict(),
        "logger": getLogger("role_manager"),
    }


def role_manager_update(client: rsk.Client, team: str, number: int, goal_sign: int, ball: array_type, data: dict) -> None:
    if is_shooter(client, team, number, goal_sign, ball):
        shooter_update(client, team, number, goal_sign, ball, data['shooter_data'])
    else:
        goalkeeper_update(client, team, number, goal_sign, ball, data['keeper_data'])
