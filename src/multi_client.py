import abc
import rsk
import util
from shooter import BaseShooterClient, MainShooterClient, RotatedShooterClient
from goalkeeper import BaseGoalKeeperClient, MainGoalKeeperClient, RotatedGoalKeeperClient
from typing import Literal, Callable



def is_shooter(client: rsk.Client, team: str, number: int, ball: util.array, goal_sign: int) -> bool:
    bot = client.robots[team][number]
    other_bot = client.robots[team][3 - number]

    if -0.46 < ball[0] * goal_sign < 0:
        return bot.position[0] * goal_sign > other_bot.position[0] * goal_sign
    elif ball[0] * goal_sign > 0:
        return True
    return False



class BaseMultiClient(util.BaseClient, abc.ABC):
    def __init__(self,
                 client: rsk.Client,
                 team: Literal['green', 'blue'],
                 number: Literal[1, 2],
                 shooter_client: BaseShooterClient,
                 keeper_client: BaseGoalKeeperClient,
                 ) -> None:
        super().__init__(client, team)
        self.number = number
        self.shooter_client = shooter_client
        self.keeper_client = keeper_client

        self.shooter_client.shooter = self.client.robots[team][number]
        self.keeper_client.keeper = self.client.robots[team][number]

    def get_client(self) -> util.BaseClient:
        if is_shooter(self.client, self.shooter_client.shooter.team, self.number, self.ball, self.goal_sign()):
            return self.shooter_client
        return self.keeper_client

    def update(self) -> None:
        self.get_client().update()

    def startup(self) -> None:
        self.logger.info(f"Running {self.__class__}.startup()...")
        self.get_client().startup()

    def on_pause(self) -> None:
        self.logger.info(f"Running {self.__class__}.on_pause()...")
        self.get_client().on_pause()


class MainMultiClient(BaseMultiClient):
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue'], number: Literal[1, 2],):
        super().__init__(client, team, number, MainShooterClient(client, team), MainGoalKeeperClient(client, team))

    def goal_sign(self) -> Literal[1, -1]:
        return 1


class RotatedMultiClient(BaseMultiClient):
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue'], number: Literal[1, 2],):
        super().__init__(client, team, number, RotatedShooterClient(client, team), RotatedGoalKeeperClient(client, team))

    def goal_sign(self) -> Literal[1, -1]:
        return -1