import rsk
import abc
import sys
import math
import argparse
import numpy as np
from logging import Logger
from typing import Literal, Sequence, Callable


type array = np.ndarray[tuple[int, ...], np.dtype[np.floating]]


def faces_ball(robot: rsk.client.ClientRobot, ball: array, threshold: int = 10) -> bool:
    """
    Takes in a robot and a threshold and returns whether the robot is pointing at the ball
    :param robot: robot object to be used for calculations
    :param ball: position of the ball
    :param threshold: margin of error in degrees, default is 10, meaning that this function still returns True
        if there is a difference of 10° or less between tha angles of the ball and the robot
    :return: True if the robot is in front of the ball within the given threshold else False
    """
    ball_angle: int = (round(math.degrees(angle_of(ball - robot.position))) + 360) % 360
    shooter_angle: int = round(math.degrees(robot.orientation)) % 360
    return -abs(threshold) <= shooter_angle - ball_angle <= abs(threshold)


def is_inside_circle(point: array, center: array, radius: float) -> bool:
    """
    :param point: Point to be checked
    :param center: Center of the circle (x,y)
    :param radius: Radius of the circle
    :return: True if point is in the circle, else False
    """
    return np.linalg.norm(center - point) <= radius


def is_inside_rect(point: Sequence[float] | array, bottomleft: Sequence[float] | array, topright: Sequence[float] | array) -> bool:
    """
    :param point: Point to be checked
    :param bottomleft: Bottom left of the rectangle (x,y)
    :param topright: Top right fo the rectangle (x,y)
    :return: Whether point is inside the rect defined by bottomleft and topright
    """
    return bottomleft[0] <= point[0] <= topright[0] and bottomleft[1] <= point[1] <= topright[1]


def is_inside_court(x: Sequence[float] | array) -> bool:
    """
    :param x: The position to be checked
    :return: Whether x is inside the in-game court
    """
    return -rsk.constants.field_length / 2 < x[0] < rsk.constants.field_length/2 and -rsk.constants.field_width / 2 < x[1] < rsk.constants.field_width/2


def is_inside_right_zone(x: Sequence[float] | array) -> bool:
    """
    :param x: The position to be checked
    :return: Whether x is inside the right goal zone
    """
    return x[0] >= rsk.constants.field_length/2 - rsk.constants.defense_area_length and rsk.constants.defense_area(True)[0][1] <= x[1] <= rsk.constants.defense_area(True)[1][1]


def is_inside_left_zone(x: Sequence[float] | array) -> bool:
    """
    :param x: The position to be checked
    :return: Whether x is inside the left goal zone
    """
    return x[0] <= -rsk.constants.field_length/2 + rsk.constants.defense_area_length and -rsk.constants.defense_area_width/2 <= x[1] <= rsk.constants.defense_area_width/2


def angle_of(pos: Sequence[float] | array) -> float:
    """
    :param pos: Vector2-like object (numpy array, list, tuple...)
    :return: the angle of pos, between -pi and +pi
    """
    return math.atan2(pos[1], pos[0])


def normalized(a: np.typing.ArrayLike) -> array:
    """
    :param a: Either a numpy array of sequence of two floats (list, tuple...), should represent a vector
    :return: the same vector but with length 1
    """
    return np.array(a) / np.linalg.norm(a)

def get_shoot_position(goal_pos: array, ball_pos: array, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    """
    :param goal_pos: Position of the goal (x,y), needs to be a numpy array
    :param ball_pos: Position of the ball (x,y), needs  to be a numpy array
    :param shooter_offset_scale: Scale at which the distance between the goal and the ball is multiplied before being applied
    :return: A tuple of three floats containing the position and the angle needed to score a goal to goal pos,
        ready to be used with goto()
    """
    #finding the shooter pos
    ball_to_goal_vector = goal_pos - ball_pos
    shooter_pos: array = ball_to_goal_vector * -shooter_offset_scale + goal_pos
    return shooter_pos[0], shooter_pos[1], angle_of(ball_to_goal_vector)

def get_alignment(pos1: array, pos2: array, base: array) -> float:
    """
    Takes three positions and returns the aligment rate between the 3.
    :param pos1: Position of the first point
    :param pos2: Position of the second point
    :param base: Center position for calculations
    :return: The angle between the base->pos1 vector and the base->pos2 vector
    """
    return abs(angle_of(pos1 - base) - angle_of(pos2 - base))

def line_intersects_circle(linepoint1: array, linepoint2: array, center: array, radius: float) -> bool:
    """
    Checkes the collision between a line and a circle
    :param linepoint1: first point of the line, must be a numpy array
    :param linepoint2: second point of the line, must be a numpy array
    :param center: center of the circle
    :param radius: radius of the circle
    :return: Whether the segment between linepoint1 and linepoint2 intersects with the circle defined by center and radius
    """
    line_vector = linepoint2 - linepoint1
    t = np.dot(center - linepoint1, line_vector) / np.linalg.norm(line_vector) ** 2
    t = np.clip(t,0, 1)
    return np.linalg.norm(line_vector * t + linepoint1 - center) <= radius


def get_parser(desc: str) -> argparse.ArgumentParser:
    """
    :param desc: description of the parser
    :return: an argparse parser that can be used to launch more easily the program, run get_parser().print_help()
    or check the argparse docs for more info
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-t', '--team', type=str, choices=('blue', 'green'), default='blue', help="team of the shooter (either 'blue' as default or 'green')")
    parser.add_argument('-H', '--host', type=str, default="127.0.0.1", help="host of the client, localhost by default")
    parser.add_argument('-k', '--key', type=str, default="", help="key of the client, empty by default")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')
    return parser



class BaseClient(abc.ABC):
    """
    Top of the class hierarchy
    Contains common code for all clients and abstract methods to be overridden by subclasses
    Provides an interface for all clients classes
    """
    @abc.abstractmethod
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue']) -> None:
        self.client = client
        self.logger: Logger = Logger(self.__class__.__name__)
        self.referee: dict = self.client.referee
        self.team = team

    def goal_sign(self) -> Literal[1, -1]:
        return -1 if self.client.referee['teams'][self.team]['x_positive'] else 1

    @abc.abstractmethod
    def update(self) -> None:
        """
        main method of the client, should be called inside a while loop
        """

    @property
    def ball(self) -> array:
        """
        provides easy access to the ball, may raise a rsk.client.CLientError if the ball cannot be found
        :return: the position of the ball
        """
        if self.client.ball is None:
            raise rsk.client.ClientError("#ball is none")
        return self.client.ball

    def is_inside_defense_zone(self, pos: Sequence[float]) -> bool:
        """
        Uses the goal_sign() method to know if a point is inside the client's defense zone
        :param pos: position of the point to be checked
        :return: True if the point is inside the defense zone else False
        """
        if self.goal_sign() == 1:
            return is_inside_left_zone(pos)
        return is_inside_right_zone(pos)



def start_client(ClientClass: Callable[[rsk.Client, Literal['green', 'blue']], BaseClient], args: list[str] | None = None):
    """
    Takes one class/function/object returning a BaseClient object and runs them automatically without any further intervention, even during the halftime.
    :param ClientClass: Callable returning BaseClient type object.
    :param args: arguments used by the parser specified in get_parser(), the function takes arguments directly from sys.argv if this argument is not specified
    :return:
    """
    arguments = get_parser("Script that runs a client (adapted to halftime change)").parse_args(sys.argv[1::] if args is None else args)
    logger = Logger("client_loader")
    logger.info(f"args: {arguments}")
    team = arguments.team

    with rsk.Client(host=arguments.host, key=arguments.key) as c:  # tkt c un bordel mais touche pas ca marche nickel
        client = ClientClass(c, team)
        while True:
            try:
                client.update()
            except rsk.client.ClientError as e:
                if arguments.verbose and repr(e)[0] != "#":
                    client.logger.warn(e)
            except KeyboardInterrupt:
                sys.exit(0)


if __name__ == "__main__":
    a, b = np.array([1, 2])
    print(a, b)
