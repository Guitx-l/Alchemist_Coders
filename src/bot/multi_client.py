import rsk
from src.util.log import getLogger
from src.bot import can_play, get_goal_sign
from src.bot.shooter import shooter_update, get_shooter_dict
from src.bot.goalkeeper import goalkeeper_update, get_keeper_dict

def is_shooter(client: rsk.Client, team: str, number: int, goal_sign: int, ball) -> bool:
    bot = client.robots[team][number]
    other_bot = client.robots[team][3 - number]

    if not can_play(other_bot, client.referee):
        return ball[0] * goal_sign > 0
    return bot.position[0] * goal_sign > other_bot.position[0] * goal_sign


def get_multi_bot_dict() -> dict:
    return {
        "shooter_data": get_shooter_dict(),
        "keeper_data": get_keeper_dict(),
        "logger": getLogger("multi_client"),
    }

def multi_update(client: rsk.Client, team: str, number: int, data: dict) -> None:
    if is_shooter(client, team, number, get_goal_sign(client, team), client.ball):
        shooter_update(client, team, number, data['shooter_data'])
    else:
        goalkeeper_update(client, team, number, data['keeper_data'])
