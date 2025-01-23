import numpy as np
from rsk import constants


goal_pos = np.array([constants.field_length / 2, 0])
shooter_offset = .15
robot_radius = constants.robot_radius + 0.1 # + 10cm