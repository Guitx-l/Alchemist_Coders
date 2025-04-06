import rsk
import math
from pygame import Vector2


def angle_of(pos) -> float:
    return math.atan2(pos[1], pos[0])

def simple_goalkeeper(team: str, rotated: bool = False):
    with rsk.Client() as client:
        while True:
            print((round(math.degrees(angle_of(client.ball - client.blue1.position))) + 360) % 360 - round(math.degrees(client.blue1.orientation)) % 360, round(Vector2(*(client.ball - client.blue1.position)).length() * 100))

if __name__ == '__main__':
    simple_goalkeeper("blue")
