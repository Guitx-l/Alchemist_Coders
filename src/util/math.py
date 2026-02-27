import rsk
import math
import numpy as np
from typing import Sequence
from src.util import array_type


def faces_ball(robot: rsk.client.ClientRobot, ball: array_type, margin: float = 0.02) -> bool:
    """
    :description: Prend un robot et une marge et retourne si le robot pointe vers le ballon
    :param robot: objet robot à utiliser pour les calculs
    :param ball: position du ballon
    :param margin: marge d'erreur en mètres, par défaut 0.02, ce qui signifie que cette fonction retourne toujours True
        si la distance entre le ballon et la ligne définie par la position et l'orientation du robot est inférieure à 2 cm
        plus le rayon du ballon
    :return: True si le robot est orienté vers le ballon dans la limite de la marge donnée, sinon False
    """
    return line_intersects_circle(
        linepoint1=robot.position, 
        linepoint2=robot.position + np.array([math.cos(robot.orientation), math.sin(robot.orientation)]), 
        center=ball, 
        radius=margin + rsk.constants.ball_radius
    )

def is_inside_circle(point: array_type, center: array_type, radius: float) -> bool:
    """
    :param point: Point à vérifier
    :param center: Centre du cercle (x,y)
    :param radius: Rayon du cercle
    :return: True si le point est dans le cercle, sinon False
    """
    return np.linalg.norm(center - point) <= radius


def is_inside_court(x: Sequence[float] | array_type) -> bool:
    """
    :param x: La position à vérifier (x, y)
    :return: Si x est à l'intérieur du terrain de jeu
    """
    return -rsk.constants.field_length / 2 < x[0] < rsk.constants.field_length/2 and -rsk.constants.field_width / 2 < x[1] < rsk.constants.field_width/2


def is_inside_right_zone(x: Sequence[float] | array_type) -> bool:
    """
    :param x: La position à vérifier (x, y)
    :return: Si x est à l'intérieur de la zone de but droit
    """
    return x[0] >= rsk.constants.field_length/2 - rsk.constants.defense_area_length and rsk.constants.defense_area(True)[0][1] <= x[1] <= rsk.constants.defense_area(True)[1][1]


def is_inside_left_zone(x: Sequence[float] | array_type) -> bool:
    """
    :param x: La position à vérifier (x, y)
    :return: Si x est à l'intérieur de la zone de but gauche
    """
    return x[0] <= -rsk.constants.field_length/2 + rsk.constants.defense_area_length and -rsk.constants.defense_area_width/2 <= x[1] <= rsk.constants.defense_area_width/2


def angle_of(pos: Sequence[float] | array_type) -> float:
    """
    :param pos: N'importe quoi qui ressemble à un vecteur (tableau numpy, liste, tuple...)
    :return: l'angle de pos, entre -pi et +pi
    """
    return math.atan2(pos[1], pos[0])


def normalized(a: np.typing.ArrayLike) -> array_type:
    """
    :param a: N'importe quoi qui ressemble à un vecteur (tableau numpy, liste, tuple...)
    :return: le même vecteur mais avec une longueur de 1
    """
    return np.array(a) / np.linalg.norm(a)


def get_shoot_position(goal_pos: array_type, ball_pos: array_type, shooter_offset: float = 1) -> tuple[float, float, float]:
    """
    :param goal_pos: Position du but (x,y), doit être un tableau numpy
    :param ball_pos: Position du ballon (x,y), doit être un tableau numpy
    :param shooter_offset: Distance ajoutée entre le ballon et la position du tireur
    :return: Un tuple de trois flottants contenant la position et l'angle nécessaires pour marquer dans le but,
        prêt à être utilisé avec goto()
    """
    goal_to_ball_vector = ball_pos - goal_pos
    vector_length = np.linalg.norm(goal_to_ball_vector)
    length_multiplier = (vector_length + shooter_offset) / vector_length
    return (
        goal_to_ball_vector[0] * length_multiplier + goal_pos[0], 
        goal_to_ball_vector[1] * length_multiplier + goal_pos[1], 
        angle_of(-goal_to_ball_vector)
    )


def get_misalignment(pos1: array_type, pos2: array_type, base: array_type) -> float:
    """
    :description: Calcule l'angle entre les vecteurs base->pos1 et base->pos2
    :param pos1: Position du premier point
    :param pos2: Position du deuxième point
    :param base: Position du centre pour les calculs
    :return: L'angle entre le vecteur base->pos1 et le vecteur base->pos2
    """
    return abs(angle_of(pos1 - base) - angle_of(pos2 - base))


def line_intersects_circle(linepoint1: array_type, linepoint2: array_type, center: array_type, radius: float) -> bool:
    """
    :description: Vérifie si le segment de ligne défini par linepoint1 et linepoint2 intersecte le cercle défini par center et radius
    :param linepoint1: premier point de la ligne, doit être un tableau numpy
    :param linepoint2: deuxième point de la ligne, doit être un tableau numpy
    :param center: centre du cercle
    :param radius: rayon du cercle
    :return: Si le segment entre linepoint1 et linepoint2 intersecte le cercle défini par center et radius
    """
    return np.linalg.norm(project_on_line(center, linepoint1, linepoint2) - center) <= radius


def project_on_line(point: array_type, line_point1: array_type, line_point2: array_type, segment: bool = True) -> array_type:
    """
    :description: Projette un point sur une ligne définie par deux points
    :param point: point à projeter, doit être un tableau numpy
    :param line_point1: premier point de la ligne, doit être un tableau numpy
    :param line_point2: deuxième point de la ligne, doit être un tableau numpy
    :param segment: s'il faut considérer la ligne comme un segment (limiter la projection entre line_point1 et line_point2)
    :return: Le point projeté sur la ligne (tableau numpy)
    """
    line_vector = line_point2 - line_point1
    t = np.dot(point - line_point1, line_vector) / np.linalg.norm(line_vector) ** 2
    if segment:
        t = np.clip(t, 0, 1)
    return line_vector * t + line_point1
