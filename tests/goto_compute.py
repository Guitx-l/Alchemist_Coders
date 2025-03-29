import rsk
import keyboard
import math
from pygame import Vector2

def main() -> None:
    with rsk.Client() as client:
        while True:
            if keyboard.is_pressed("d"):
                client.blue1.control(0, 0, -1)
            elif keyboard.is_pressed("q"):
                client.blue1.control(0, 0, 1)
            elif keyboard.is_pressed("space"):
                ball_angle: int = round(math.degrees(math.atan2(*Vector2(*(client.ball - client.blue1.position)).yx)))
                print(round(math.degrees(client.blue1.orientation)) % 360 - (ball_angle + 360) % 360)
            else:
                client.blue1.control(0, 0, 0)



if __name__ == '__main__':
    main()
