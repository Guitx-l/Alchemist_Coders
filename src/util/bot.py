import rsk
from src.util.math import array_type


def can_play(bot: rsk.client.ClientRobot, referee: dict) -> bool:
    return (not referee['teams'][bot.team]['robots'][str(bot.number)]['preempted']) and (not referee['teams'][bot.team]['robots'][str(bot.number)]['penalized'])





def get_robot(client: rsk.Client, team: str, number: int) -> rsk.client.ClientRobot:
    robot = client.robots[team][number]
    if not robot.has_position(skip_old=True):
        raise rsk.client.ClientError(f"#Impossible de trouver le robot {team}{number}.")
    return robot