import abc
import rsk
import util
import math
from typing import Literal, final

class BaseGoalKeeperClient(util.BaseClient, abc.ABC):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.keeper: rsk.client.ClientRobot = client.robots[team][2]

    def startup(self) -> None:
        self.logger.info(f"Running {self.__class__}.startup()...")

    def on_pause(self) -> None:
        self.logger.info(f"Running {self.__class__}.on_pause()...")

    def get_opposing_shooter(self) -> rsk.client.ClientRobot:
        opposing_team: str = "blue" if self.keeper.team == "green" else "green"
        if self.goal_sign() == 1:
            if self.client.robots[opposing_team][1].position[0] < self.client.robots[opposing_team][2].position[0]:
                return self.client.robots[opposing_team][1]
            return self.client.robots[opposing_team][2]
        else:
            if self.client.robots[opposing_team][1].position[0] > self.client.robots[opposing_team][2].position[0]:
                return self.client.robots[opposing_team][1]
            return self.client.robots[opposing_team][2]

    @final
    def update(self) -> None:
        if util.is_inside_court(self.ball):
            if self.is_inside_defense_zone(self.ball):
                self.keeper.goto((self.ball[0], self.ball[1], self.keeper.orientation), wait=False)
            else:
                shooter_pos = self.get_opposing_shooter().position
                y_keeper = (self.ball[1] - shooter_pos[1]) / (self.ball[0] - shooter_pos[0]) * (-self.goal_sign() - self.ball[0]) + self.ball[1]
                self.keeper.goto((-self.goal_sign(), y_keeper, math.pi if self.goal_sign() == -1 else 0), wait=False)

            if util.is_inside_circle(self.ball, self.keeper.position, 0.15):
                self.keeper.kick(1)

class MainGoalKeeperClient(BaseGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return 1

class RotatedGoalKeeperClient(BaseGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return -1

if __name__ == "__main__":
    util.start_client(MainGoalKeeperClient, RotatedGoalKeeperClient)
