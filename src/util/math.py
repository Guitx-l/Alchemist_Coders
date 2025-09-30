import rsk
import math
import numpy as np
from typing import Sequence
from .__init__ import array_type

def faces_ball(robot: rsk.client.ClientRobot, ball: array_type, threshold: int = 10) -> bool:
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


def is_inside_circle(point: array_type, center: array_type, radius: float) -> bool:
    """
    :param point: Point to be checked
    :param center: Center of the circle (x,y)
    :param radius: Radius of the circle
    :return: True if point is in the circle, else False
    """
    return np.linalg.norm(center - point) <= radius


def is_inside_court(x: Sequence[float] | array_type) -> bool:
    """
    :param x: The position to be checked
    :return: Whether x is inside the in-game court
    """
    return -rsk.constants.field_length / 2 < x[0] < rsk.constants.field_length/2 and -rsk.constants.field_width / 2 < x[1] < rsk.constants.field_width/2


def is_inside_right_zone(x: Sequence[float] | array_type) -> bool:
    """
    :param x: The position to be checked
    :return: Whether x is inside the right goal zone
    """
    return x[0] >= rsk.constants.field_length/2 - rsk.constants.defense_area_length and rsk.constants.defense_area(True)[0][1] <= x[1] <= rsk.constants.defense_area(True)[1][1]


def is_inside_left_zone(x: Sequence[float] | array_type) -> bool:
    """
    :param x: The position to be checked
    :return: Whether x is inside the left goal zone
    """
    return x[0] <= -rsk.constants.field_length/2 + rsk.constants.defense_area_length and -rsk.constants.defense_area_width/2 <= x[1] <= rsk.constants.defense_area_width/2


def angle_of(pos: Sequence[float] | array_type) -> float:
    """
    :param pos: Vector2-like object (numpy array, list, tuple...)
    :return: the angle of pos, between -pi and +pi
    """
    return math.atan2(pos[1], pos[0])


def normalized(a: np.typing.ArrayLike) -> array_type:
    """
    :param a: Either a numpy array of sequence of two floats (list, tuple...), should represent a vector
    :return: the same vector but with length 1
    """
    return np.array(a) / np.linalg.norm(a)

def get_shoot_position(goal_pos: array_type, ball_pos: array_type, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    """
    :param goal_pos: Position of the goal (x,y), needs to be a numpy array
    :param ball_pos: Position of the ball (x,y), needs  to be a numpy array
    :param shooter_offset_scale: Scale at which the distance between the goal and the ball is multiplied before being applied
    :return: A tuple of three floats containing the position and the angle needed to score a goal to goal pos,
        ready to be used with goto()
    """
    #finding the shooter pos
    ball_to_goal_vector = goal_pos - ball_pos
    shooter_pos: array_type = ball_to_goal_vector * -shooter_offset_scale + goal_pos
    return shooter_pos[0], shooter_pos[1], angle_of(ball_to_goal_vector)

def get_alignment(pos1: array_type, pos2: array_type, base: array_type) -> float:
    """
    Takes three positions and returns the aligment rate between the 3.
    :param pos1: Position of the first point
    :param pos2: Position of the second point
    :param base: Center position for calculations
    :return: The angle between the base->pos1 vector and the base->pos2 vector
    """
    return abs(angle_of(pos1 - base) - angle_of(pos2 - base))

def line_intersects_circle(linepoint1: array_type, linepoint2: array_type, center: array_type, radius: float) -> bool:
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