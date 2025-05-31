import time
import numpy as np
import rsk
import pynput
import pprint



def on_press(key):
    if key == pynput.keyboard.Key.space:
        with rsk.Client() as client:
            pprint.pprint(client.referee)

if __name__ == '__main__':
    l = pynput.keyboard.Listener(on_press=on_press)
    l.start()
    while True: continue
