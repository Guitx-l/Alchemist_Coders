import rsk
import math
import keyboard
from pygame import Vector2


def angle_of(pos) -> float:
    return math.atan2(pos[1], pos[0])

def simple_goalkeeper(team: str, rotated: bool = False):
    with rsk.Client() as client:
        while True:
            if keyboard.is_pressed("q"):
                client.blue1.control(0, 0, 0.1)
            elif keyboard.is_pressed("d"):
                client.blue1.control(0, 0, -0.1)
            print(round(math.degrees(client.blue1.orientation)) % 360, round(Vector2(*(client.ball - client.blue1.position)).length() * 100))

if __name__ == '__main__':
    simple_goalkeeper("blue")
