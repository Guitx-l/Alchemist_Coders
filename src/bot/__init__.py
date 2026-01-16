"""
La ou ya tous les bots
"""

import rsk
import logging
import dataclasses
from typing import Literal, Sequence
from src.util.log import getLogger
from src.util.math import is_inside_left_zone, is_inside_right_zone
from src.util import array_type


def can_play(bot: rsk.client.ClientRobot, referee: dict) -> bool:
    return (not referee['teams'][bot.team]['robots'][str(bot.number)]['preempted']) and (not referee['teams'][bot.team]['robots'][str(bot.number)]['penalized'])

@dataclasses.dataclass
class BotData:
    client: rsk.Client
    team: Literal['green', 'blue']
    logger: logging.Logger = dataclasses.field(init=False)

    def __post_init__(self):
        self.logger: logging.Logger = getLogger(self.__class__.__name__)

    def goal_sign(self) -> Literal[1, -1]:
        return -1 if self.client.referee['teams'][self.team]['x_positive'] else 1

    @property
    def ball(self) -> array_type:
        """
        provides easy access to the ball, may raise a rsk.client.ClientError if the ball cannot be found
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
