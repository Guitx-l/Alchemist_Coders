import rsk
import numpy as np
from typing import Sequence

type array_type = np.ndarray[tuple[int, ...], np.dtype[np.floating]]

HALF_FIELD_LENGTH = rsk.constants.field_length / 2
HALF_FIELD_WIDTH = rsk.constants.field_width / 2
HALF_DEFENSE_AREA_WIDTH = rsk.constants.defense_area_width / 2


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
    cos_o = np.cos(robot.orientation)
    sin_o = np.sin(robot.orientation)
    return line_intersects_circle(
        linepoint1=robot.position,
        linepoint2=np.array([robot.position[0] + cos_o, robot.position[1] + sin_o]),
        center=ball,
        radius=margin + rsk.constants.ball_radius
    )

def is_inside_circle(point: array_type, center: array_type, radius: float) -> bool:
    """
    :param point: Point à vérifier, doit être un tableau numpy
    :param center: Centre du cercle (x,y), doit être un tableau numpy
    :param radius: Rayon du cercle
    :return: True si le point est dans le cercle, sinon False
    """
    return bool(np.linalg.norm(center - point) <= radius)


def is_inside_court(x: Sequence[float] | array_type) -> bool:
    """
    :param x: La position à vérifier (x, y)
    :return: Si x est à l'intérieur du terrain de jeu
    """
    return -HALF_FIELD_LENGTH < x[0] < HALF_FIELD_LENGTH and -HALF_FIELD_WIDTH < x[1] < HALF_FIELD_WIDTH


def is_inside_right_zone(x: Sequence[float] | array_type) -> bool:
    """
    :param x: La position à vérifier (x, y)
    :return: Si x est à l'intérieur de la zone de but droit
    """
    return x[0] >= HALF_FIELD_LENGTH - rsk.constants.defense_area_length and -HALF_DEFENSE_AREA_WIDTH <= x[1] <= HALF_DEFENSE_AREA_WIDTH


def is_inside_left_zone(x: Sequence[float] | array_type) -> bool:
    """
    :param x: La position à vérifier (x, y)
    :return: Si x est à l'intérieur de la zone de but gauche
    """
    return x[0] <= -HALF_FIELD_LENGTH + rsk.constants.defense_area_length and -HALF_DEFENSE_AREA_WIDTH <= x[1] <= HALF_DEFENSE_AREA_WIDTH


def angle_of(pos: Sequence[float] | array_type) -> float:
    """
    :param pos: N'importe quoi qui ressemble à un vecteur (tableau numpy, liste, tuple...)
    :return: l'angle de pos, entre -pi et +pi
    """    
    return np.arctan2(pos[1], pos[0])


def normalized(a: np.typing.ArrayLike) -> array_type:
    """
    :param a: N'importe quoi qui ressemble à un vecteur (tableau numpy, liste, tuple...)
    :return: le même vecteur mais avec une longueur de 1
    """
    return np.array(a) / np.linalg.norm(a)


def get_shoot_position(goal_pos: array_type, ball_pos: array_type, shooter_offset: float = 0) -> tuple[float, float, float]:
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

def get_angle_between(vector1: array_type, vector2: array_type) -> float:
    """
    :param vector1: Premier vecteur (x,y), doit être un tableau numpy
    :param vector2: Deuxième vecteur (x,y), doit être un tableau numpy
    :return: L'angle entre les deux vecteurs, entre 0 et +pi
    """
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.arccos(np.clip(np.dot(vector1, vector2) / (norm1 * norm2), -1.0, 1.0))


def line_intersects_circle(linepoint1: array_type, linepoint2: array_type, center: array_type, radius: float) -> bool:
    """
    :description: Vérifie si le segment de ligne défini par linepoint1 et linepoint2 intersecte le cercle défini par center et radius
    :param linepoint1: premier point de la ligne, doit être un tableau numpy
    :param linepoint2: deuxième point de la ligne, doit être un tableau numpy
    :param center: centre du cercle
    :param radius: rayon du cercle
    :return: Si le segment entre linepoint1 et linepoint2 intersecte le cercle défini par center et radius
    """
    return bool(np.linalg.norm(project_on_line(center, linepoint1, linepoint2) - center) <= radius)

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
