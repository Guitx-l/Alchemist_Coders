import rsk
from typing import Iterable
import numpy as np


class Referee:
    def __init__(self, referee: dict):
        self.__dict__ = referee.copy()


class Robots:
    def __init__(self, robots: dict[str, dict]):
        self.robots = robots
        self.indexes = (
            ("green", 1),
            ("green", 2),
            ("blue", 1),
            ("blue", 2)
        )
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self) -> rsk.client.ClientRobot:
        self.index += 1
        if self.index > 3:
            raise StopIteration
        i = self.indexes[self.index]
        return self.robots[i[0]][i[1]]


def is_inside_circle(point: np.ndarray[float], center: np.ndarray[float], radius: float) -> bool:
    return sum((center - point) ** 2) <= radius ** 2


def is_inside_rect(point: Iterable[float], bottomleft: Iterable[float], topright: Iterable[float]) -> bool:
    return bottomleft[0] <= point[0] <= topright[0] and bottomleft[1] <= point[1] <= topright[1]


def is_inside_court(x: np.ndarray) -> bool:
    return -rsk.constants.field_length / 2 < x[0] < rsk.constants.field_length/2 and -rsk.constants.field_width / 2 < x[1] < rsk.constants.field_width/2


if __name__ == "__main__":
    pass
