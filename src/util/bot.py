import rsk
from typing import Literal, Sequence
import logging
import abc
from .log import getLogger
from .math import is_inside_left_zone, is_inside_right_zone
from .__init__ import *


def can_play(bot: rsk.client.ClientRobot, referee: dict) -> bool:
    return (not referee['teams'][bot.team]['robots'][str(bot.number)]['preempted']) and (not referee['teams'][bot.team]['robots'][str(bot.number)]['penalized'])

class BaseClient(abc.ABC):
    """
    Top of the class hierarchy
    Contains common code for all clients and abstract methods to be overridden by subclasses
    Provides an interface for all clients classes
    """
    @abc.abstractmethod
    def __init__(self, client: rsk.Client, team: Literal['green', 'blue']) -> None:
        self.client = client
        self.team = team
        self.logger: logging.Logger = getLogger(self.__class__ .__name__)
        self.referee: dict = self.client.referee
        self.logger.setLevel(logging.DEBUG)

    def goal_sign(self) -> Literal[1, -1]:
        return -1 if self.client.referee['teams'][self.team]['x_positive'] else 1

    @abc.abstractmethod
    def update(self) -> None:
        """
        main method of the client, should be called inside a while loop
        """

    @property
    def ball(self) -> array_type:
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