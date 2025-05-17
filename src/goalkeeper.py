import abc
import sys
import time
import numpy as np
import rsk
import util
import math
from util import array
from typing import Literal, final

class BaseGoalKeeperClient(util.BaseClient, abc.ABC):
    def __init__(self, client: rsk.Client, team: Literal['blue', 'green'] = 'blue') -> None:
        super().__init__(client, team)
        self.keeper: rsk.client.ClientRobot = client.robots[team][2]
        self.last_ball_position: array = np.zeros(2)

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

    def defenseur(self):
        orientation = 2 * math.pi if self.goal_sign() == 1 else math.pi
        halftime = True
        rotated = self.goal_sign() == -1

        while self.client.ball is None:
            continue
        if self.keeper.team == "green":
            robot_adv1 = self.client.blue1
            robot_adv2 = self.client.blue2
        else:
            robot_adv1 = self.client.green1
            robot_adv2 = self.client.green2
        if orientation == 2 * math.pi:
            x_placement = -0.8
            ball_en_x = self.client.ball[0] < -0.4
        else:
            x_placement = 0.8
            ball_en_x = self.client.ball[0] > 0.4

        while True:
            if self.client.referee["halftime_is_running"]:
                if halftime:
                    orientation = 2 * math.pi if rotated else math.pi
                    rotated = not rotated
                    halftime = False
            else:
                halftime = True
            try:
                distance_ball = math.sqrt(
                    ((self.client.ball[0] - self.keeper.pose[0]) ** 2) + ((self.client.ball[1] - self.keeper.pose[1]) ** 2))
                ball_en_x = distance_ball < 0.6

            except Exception as e:
                pass#print("Erreur gestion_des_robots def : " + str(e))

            try:
                if self.client.ball is None:
                    raise Exception
                choix_de_defense = 0

                self.keeper.goto((x_placement, self.client.ball[1], orientation), wait=False)

                if choix_de_defense == 0:

                    if ball_en_x:
                        self.keeper.goto((self.client.ball[0], self.client.ball[1], orientation), wait=True)
                        self.keeper.kick(1.0)
                        self.keeper.goto((x_placement, self.client.ball[1], orientation), wait=True)
                    else:
                        distance_adverse_1 = math.sqrt(
                            ((self.client.ball[0] - robot_adv1.pose[0]) ** 2) + ((self.client.ball[1] - robot_adv1.pose[1]) ** 2))
                        distance_adverse_2 = math.sqrt(
                            ((self.client.ball[0] - robot_adv2.pose[0]) ** 2) + ((self.client.ball[1] - robot_adv2.pose[1]) ** 2))
                        if ball_en_x:
                            self.keeper.goto((self.client.ball[0], self.client.ball[1], orientation), wait=False)
                            self.keeper.kick(1.0)
                        else:
                            if distance_adverse_1 >= distance_adverse_2:
                                robot_adv_le_plus_proche = robot_adv2

                            else:
                                robot_adv_le_plus_proche = robot_adv1

                            x_defense = ((0.8) - robot_adv_le_plus_proche.pose[0])

                            angle_adv_en_radian = robot_adv_le_plus_proche.pose[2]

                            y_le_saint_des_saint = (x_defense * math.tan(angle_adv_en_radian)) + \
                                                   robot_adv_le_plus_proche.pose[1]

                            if y_le_saint_des_saint < 0.3 and y_le_saint_des_saint > -0.3:
                                self.keeper.goto((x_placement, y_le_saint_des_saint, orientation), wait=True)

                elif choix_de_defense == 1:
                    self.keeper.goto((x_placement, self.client.ball[1], orientation), wait=True)
                    if math.sqrt(((self.client.ball[0] - self.keeper.pose[0]) ** 2) + (
                            (self.client.ball[1] - self.keeper.pose[1]) ** 2)) < 0.1:
                        self.keeper.kick(1.0)
                        self.keeper.goto((self.client.ball[0] + 1, self.client.ball[1] + 1, orientation), wait=True)
                        self.keeper.goto((self.client.ball[0] - 1, self.client.ball[1] - 1, orientation), wait=True)
                        self.keeper.kick(1.0)
            except Exception as e:
                pass#print("Erreur défenseur :", e)
            #time.sleep(0.1)  # Pour éviter une boucle infinie trop rapide

    @final
    def update(self) -> None:
        if util.is_inside_court(self.ball):
            shooter_pos = self.get_opposing_shooter().position
            #y_keeper = (self.ball[1] - shooter_pos[1]) / (self.ball[0] - shooter_pos[0]) * (-self.goal_sign() - self.ball[0]) + self.ball[1]
            self.keeper.goto((-self.goal_sign() * 0.9, self.ball[1], math.pi if self.goal_sign() == -1 else 0), wait=False)

            if util.is_inside_circle(self.ball, self.keeper.position, 0.2):
                self.keeper.kick(1)

class MainGoalKeeperClient(BaseGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return 1

class RotatedGoalKeeperClient(BaseGoalKeeperClient):
    def goal_sign(self) -> Literal[1, -1]:
        return -1

def main() -> None:
    arguments = util.get_parser("").parse_args(sys.argv[1::])
    print(arguments)
    with rsk.Client(arguments.host, arguments.key) as client:
        if arguments.rotated:
            RotatedGoalKeeperClient(client, arguments.team).defenseur()
        else:
            MainGoalKeeperClient(client, arguments.team).defenseur()

if __name__ == "__main__":
    main()
