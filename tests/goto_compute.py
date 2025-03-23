import rsk
import numpy as np


def main() -> None:
    with rsk.Client() as client:
        while True:
            pos = np.array([int(i) for i in input("> ").split()])
            print(client.blue1.goto_compute_order((*pos, 0)))


if __name__ == '__main__':
    main()
