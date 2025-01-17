import math
import rsk
import numpy as np




def get_shoot_pos(goal_pos: np.ndarray, ball_pos: np.ndarray, shooter_offset: float = 0) -> tuple[float, float, float]:
    #finding the shooter pos
    shooter_pos: np.ndarray = ball_pos
    if ball_pos[0] > 0:
        shooter_pos[0] += shooter_offset
    else:
        shooter_pos[1] -= shooter_offset
    if ball_pos[0] > 0:
        shooter_pos[1] += shooter_offset
    else:
        shooter_pos[1] -= shooter_offset
            
    return (
        *shooter_pos,
        math.atan(
            abs(goal_pos[1] - shooter_pos[1]) / abs(goal_pos[0] - shooter_pos[0]))
        )
