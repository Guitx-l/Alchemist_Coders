import abc
import time
import numpy as np
import rsk
import util
import math
from util import array
from typing import Literal


class BaseGoalKeeperClient(util.BaseClient, abc.ABC):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.last_timestamp = time.time()
        self.keeper: rsk.client.ClientRobot = client.robots[team][2]
        self.last_ball_position: array = np.zeros(2)

    def startup(self) -> None:
        self.logger.info(f"Running {self.__class__}.startup()...")

    def on_pause(self) -> None:
        self.logger.info(f"Running {self.__class__}.on_pause()...")

    def get_opposing_shooter(self) -> rsk.client.ClientRobot:
        opposing_team: str = "blue" if self.keeper.team == "green" else "green"
        opp_1 = self.client.robots[opposing_team][1]
        opp_2 = self.client.robots[opposing_team][2]

        if np.linalg.norm(opp_1.position - self.ball) < np.linalg.norm(opp_2.position - self.ball):
            return opp_1
        return opp_2

    def update(self) -> None:
        target_x = -0.92 * self.goal_sign()
        target_y = self.keeper.position[1]
        strategy = ""
        if not util.is_inside_court(self.ball):
            self.keeper.goto(self.keeper.pose)
            return

        shooter = self.get_opposing_shooter().pose
        goal_post_x = -0.92 * self.goal_sign()

        if np.linalg.norm(self.ball - shooter[:2]) > 0.18 and np.linalg.norm(self.ball - self.last_ball_position) > 0.05:
            ball_vector = self.ball - self.last_ball_position
            target_y = self.ball[1] + (ball_vector[1] * (goal_post_x - self.last_ball_position[0]) / ball_vector[0])
            strategy = "thales-ball"

        elif self.faces_ball(self.get_opposing_shooter(), 20):
            target_y = shooter[1] + (math.tan(shooter[2]) * (goal_post_x - shooter[0]))
            strategy = "tan-shooter"

        elif util.get_alignment(np.array([target_x, target_y]), self.ball, shooter[:2]) < 10:
            target_y = self.ball[1] + (self.ball[1] - shooter[1]) / (self.ball[0] - shooter[0]) * (goal_post_x - self.ball[0])
            strategy = "thales-shooter"


        if not self.is_inside_defense_zone(self.ball) and self.ball[0] * self.goal_sign() < 0.1 and strategy != "":
            goal_pos = np.array([target_x, target_y])
            shoot_pos = shooter[:2] if strategy == "tan-shooter" else self.ball
            trajectory = shoot_pos - goal_pos
            new_target =  goal_pos + trajectory * (np.dot(self.keeper.position - goal_pos, trajectory) / np.linalg.norm(trajectory) ** 2)
            target_x, target_y = new_target
        else:
            target_y = np.clip(target_y, -0.25, 0.25)

        self.keeper.goto((target_x, target_y, math.pi if self.goal_sign() == -1 else 0), wait=False)

        if util.is_inside_circle(self.ball, self.keeper.position, 0.2):
            self.keeper.kick(1)

        if time.time() - self.last_timestamp >= 0.1:
            self.last_ball_position = self.ball.copy()
            self.last_timestamp = time.time()



class MainGoalKeeperClient(BaseGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return 1


class RotatedGoalKeeperClient(BaseGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return -1



if __name__ == "__main__":
    util.start_client(MainGoalKeeperClient, RotatedGoalKeeperClient)
