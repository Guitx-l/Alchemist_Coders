import rsk
from typing import Literal
from src.bot import BotData, can_play
from src.bot.shooter import ShooterData, shooter_update
from src.bot.goalkeeper import GoalKeeperData, goalkeeper_update


def is_shooter(client: rsk.Client, team: str, number: int, goal_sign: int, ball) -> bool:
    bot = client.robots[team][number]
    other_bot = client.robots[team][3 - number]

    if not can_play(other_bot, client.referee):
        return ball[0] * goal_sign > 0
    return bot.position[0] * goal_sign > other_bot.position[0] * goal_sign


class MultiBotData(BotData):
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue'], number: Literal[1, 2]) -> None:
        super().__init__(client, team)
        self.number = number
        self.shooter_data = ShooterData(self.client, self.team)
        self.keeper_data = GoalKeeperData(self.client, self.team)

        self.shooter_data.shooter = self.client.robots[self.team][self.number]
        self.keeper_data.keeper = self.client.robots[self.team][self.number]


def multi_update(data: MultiBotData) -> None:
    if is_shooter(data.client, data.team, data.number, data.goal_sign(), data.ball):
        shooter_update(data.shooter_data)
    else:
        goalkeeper_update(data.keeper_data)
