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


def startup(client: rsk.Client) -> None:
    def sub_func(*_) -> None:
        pass#print([round(i, 2) for i in [*client.ball, math.degrees(client.blue1.pose[2])]])
    client.on_update = sub_func
    if not is_preempted(client.blue1, client.referee):
        client.blue1.goto((-.15, 0, 0))
    if not is_preempted(client.green1, client.referee):
        client.green1.goto((.15, 0, 3.14))


def main(client: rsk.Client) -> None:
    ball = client.ball.copy() if client.ball is not None else np.array([0, 0])

    # defender blue
    if not is_preempted(client.blue2, client.referee):
        client.blue2.goto((-constants.defense_area_width, ball[1], 0), False)
        if ball[0] < -constants.field_length / 2 + constants.defense_area_length:
            client.blue2.kick(1)
    # defender green
    if not is_preempted(client.green2, client.referee):
        client.green2.goto((constants.defense_area_width, ball[1], 3.14), False)
        if ball[0] > constants.field_length / 2 - constants.defense_area_length:
            client.green2.kick(1)

    # shooter
    if .1 < ball[0] < constants.field_length / 2:  # si la balle se trouve dans le terrain et le cote droit
        x = sum((abs(i) for i in client.blue1.position - ball))
        print(f"distance to ball~~: {round(x, 3)}")
        if x <= .2: # si la balle se trouve dans un rayon d'environ 0.2m autour du robot
            print("KAKHJGFHN LAAAAAAAAAAAAAA")
            client.blue1.kick(1)

        # icecream.ic(ball[0])
        # client.blue1.goto(, False)
        goto = attack.get_shoot_pos(  # on déplace
            np.array([constants.field_length / 2, 0]),
            ball
        )
        print(f"goto: {np.around(goto, 3)}")
        print(f"robot: {np.around(client.blue1.pose, 3)}\n\n")
        if not is_preempted(client.blue1, client.referee):
            client.blue1.goto(goto, False)
            client.blue1.kick(1)

    if keyboard.is_pressed("q"):
        client.blue1.control(0, 0, math.radians(100))
        client.blue1.control(0, 0, 0)
    if keyboard.is_pressed("d"):
        client.blue1.control(0, 0, math.radians(-100))


if __name__ == "__main__":
    with rsk.Client() as c:
        startup(c)
        while True:
            try:
                main(c)
            except KeyboardInterrupt:
                break
