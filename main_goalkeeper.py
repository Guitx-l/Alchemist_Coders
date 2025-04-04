import abc
from typing import Literal, final
from util import array
import rsk
import util
import math

class IGoalKeeperClient(util.IClient, abc.ABC):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.keeper: rsk.client.ClientRobot = client.robots[team][2]

    def startup(self) -> None:
        self.logger.info(f"Running {self.__class__}.startup()...")

    def on_pause(self) -> None:
        self.logger.info(f"Running {self.__class__}.on_pause()...")

    @final
    def update(self) -> None:
        if util.is_inside_court(self.ball):
            self.keeper.goto((self.goal_sign(), self.ball[1], math.pi if self.goal_sign() == -1 else 0), wait=False)

class MainGoalKeeperClient(IGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return 1

class RotatedGoalKeeperClient(IGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return -1