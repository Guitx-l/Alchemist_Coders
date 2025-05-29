import time

import numpy as np
import rsk
import math
import pynput


def angle_of(pos) -> float:
    return math.atan2(pos[1], pos[0])

def on_press(key):
    with rsk.Client() as client:
        if key == pynput.keyboard.KeyCode.from_char('q'):
            client.blue1.control(0, 0, 1)
        elif key == pynput.keyboard.KeyCode.from_char('d'):
            client.blue1.control(0, 0, -1)
            print("DDDDDDD")
        elif key == pynput.keyboard.Key.space:
            client.blue1.control(0, 0, 0)
            print(client.blue1.orientation)


def simple_goalkeeper(team: str, rotated: bool = False):
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()
    while True:
        continue

if __name__ == '__main__':
    simple_goalkeeper("blue")
