import rsk
import attack
import numpy as np
from rsk import constants
import os
import time
import math
import icecream
import util
import keyboard


def is_preempted(robot: rsk.client.ClientRobot, referee: dict) -> bool:
    return referee["teams"][robot.team]["robots"][str(robot.number)]["preempted"]

class Main:
    def __init__(self, client: rsk.Client):
        self.client = client
        self.shooter: rsk.client.ClientRobot = client.blue1
        self.defender = client.blue2
        self.referee: dict = self.client.referee

    def startup(self) -> None:
        def sub_func(*_) -> None:
            pass#print([round(i, 2) for i in [*client.ball, math.degrees(client.blue1.pose[2])]])
        self.client.on_update = sub_func
        if not is_preempted(self.shooter, self.referee):
            self.shooter.goto((-.15, 0, 0))


    def main(self) -> None:
        ball = self.client.ball if self.client.ball is not None else np.array([0, 0])

        """
        # defender blue
        if not is_preempted(self.client.blue2, self.client.referee):
            client.blue2.goto((-constants.defense_area_width, ball[1], 0), False)
            if ball[0] < -constants.field_length / 2 + constants.defense_area_length:
                client.blue2.kick(1)
        """
        # shooter
        if .1 < ball[0] < constants.field_length / 2:  # si la balle se trouve dans le terrain et le cote droit
            x = sum((abs(i) for i in self.shooter.position - ball))
            print(f"distance to ball~~: {round(x, 3)}")
            if x <= .2: # si la balle se trouve dans un rayon d'environ 0.2m autour du robot
                print("KAKHJGFHN LAAAAAAAAAAAAAA")
                self.shooter.kick(1)

            # icecream.ic(ball[0])
            # client.blue1.goto(, False)
            goto = attack.get_shoot_pos(  # on déplace
                np.array([constants.field_length / 2, 0]),
                ball
            )
            print(f"goto: {np.around(goto, 3)}")
            print(f"robot: {np.around(self.shooter.pose, 3)}\n\n")
            if not is_preempted(self.shooter, self.client.referee):
                self.shooter.goto(goto, False)
                self.shooter.kick(1)

        if keyboard.is_pressed("q"):
            self.shooter.control(0, 0, math.radians(100))
            self.shooter.control(0, 0, 0)
        if keyboard.is_pressed("d"):
            self.shooter.control(0, 0, math.radians(-100))


if __name__ == "__main__":
    with rsk.Client() as c:
        main = Main(c)
        main.startup()
        while True:
            try:
                main.main()
            except KeyboardInterrupt:
                break
