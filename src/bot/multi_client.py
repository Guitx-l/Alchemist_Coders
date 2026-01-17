import rsk
import dataclasses
from typing import Literal
from src.bot import BotData, can_play
from src.bot.shooter import ShooterData, update as shooter_update
from src.bot.goalkeeper import GoalKeeperData, update as goalkeeper_update


def is_shooter(client: rsk.Client, team: str, number: int, goal_sign: int, ball) -> bool:
    bot = client.robots[team][number]
    other_bot = client.robots[team][3 - number]

    if not can_play(other_bot, client.referee):
        return ball[0] * goal_sign > 0
    return bot.position[0] * goal_sign > other_bot.position[0] * goal_sign


@dataclasses.dataclass
class MultiBotData(BotData):
    number: Literal[1, 2] = 1
    shooter_data: ShooterData = dataclasses.field(init=False)
    keeper_data: GoalKeeperData = dataclasses.field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.shooter_data = ShooterData(self.client, self.team)
        self.keeper_data = GoalKeeperData(self.client, self.team)

        self.shooter_data.shooter = self.client.robots[self.team][self.number]
        self.keeper_data.keeper = self.client.robots[self.team][self.number]


def update(data: MultiBotData) -> None:
    if is_shooter(data.client, data.team, data.number, data.goal_sign(), data.ball):
        return shooter_update(data.shooter_data)
    goalkeeper_update(data.keeper_data)


