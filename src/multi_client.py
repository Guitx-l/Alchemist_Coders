import abc
import rsk
import util
from shooter import BaseShooterClient, MainShooterClient, RotatedShooterClient
from goalkeeper import BaseGoalKeeperClient, MainGoalKeeperClient, RotatedGoalKeeperClient
from typing import Literal, Callable

class BaseMultiClient(util.BaseClient, abc.ABC):
    def __init__(self,
                 client: rsk.Client,
                 team: Literal['green', 'blue'],
                 number: Literal[1, 2],
                 shooter_client: BaseShooterClient,
                 keeper_client: BaseGoalKeeperClient,
                 is_shooter: Callable[[util.array, int], bool] | None = None
                 ) -> None:
        super().__init__(client, team)
        self.number = number
        self.shooter_client = shooter_client
        self.keeper_client = keeper_client

        if is_shooter:
            self.is_shooter = is_shooter
        elif number == 1:
            self.is_shooter = lambda ball, goal_sign: ball[0] * goal_sign > -0.46
        else:
            self.is_shooter = lambda ball, goal_sign: ball[0] * goal_sign > 0

        self.shooter_client.shooter = self.client.robots[team][number]
        self.keeper_client.keeper = self.client.robots[team][number]

    def get_client(self) -> util.BaseClient:
        if self.is_shooter(self.ball, self.goal_sign()):
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


class RotatedMultiCLient(BaseMultiClient):
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue'], number: Literal[1, 2],):
        super().__init__(client, team, number, RotatedShooterClient(client, team), RotatedGoalKeeperClient(client, team))

    def goal_sign(self) -> Literal[1, -1]:
        return -1