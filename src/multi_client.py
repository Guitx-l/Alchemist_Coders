import abc
import rsk
import util
from shooter import ShooterClient
from goalkeeper import GoalKeeperClient
from typing import Literal



def is_shooter(client: rsk.Client, team: str, number: int, ball: util.array, goal_sign: int) -> bool:
    bot = client.robots[team][number]
    other_bot = client.robots[team][3 - number]

    if -0.46 <= ball[0] * goal_sign <= 0.3:
        return bot.position[0] * goal_sign > other_bot.position[0] * goal_sign
    elif ball[0] * goal_sign > 0:
        return True
    return False



class BaseMultiClient(util.BaseClient):
    def __init__(self,
                 client: rsk.Client,
                 team: Literal['green', 'blue'],
                 number: Literal[1, 2],
                 ) -> None:
        super().__init__(client, team)
        self.number = number
        self.shooter_client = ShooterClient(client, team)
        self.keeper_client = GoalKeeperClient(client, team)

        self.shooter_client.shooter = self.client.robots[team][number]
        self.keeper_client.keeper = self.client.robots[team][number]

    def get_client(self) -> util.BaseClient:
        if is_shooter(self.client, self.shooter_client.shooter.team, self.number, self.ball, self.goal_sign()):
            return self.shooter_client
        return self.keeper_client

    def update(self) -> None:
        self.get_client().update()
