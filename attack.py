import math
import rsk
import numpy as np




def get_shoot_pos(goal_pos: np.ndarray, ball_pos: np.ndarray, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    #finding the shooter pos
    ball_to_goal_vec = goal_pos - ball_pos
    shooter_pos: np.ndarray = ball_to_goal_vec * -shooter_offset_scale + goal_pos

    return (*shooter_pos, math.atan2(*reversed(ball_to_goal_vec)))
