import rsk
import time
import numpy as np
from collections import deque
from threading import Lock
from src.util.math import get_angle_between

QUEUE_UPDATE_PERIOD =  1 / 30 # en s / update
LOOKBACK_TIME = 0.2 # en s
LOOKBACK_FRAMES = int(LOOKBACK_TIME / QUEUE_UPDATE_PERIOD) # 6 updates a 30Hz
KICK_DETECTION_ANGLE_THRESHOLD = np.radians(60) # en radians

QUEUE_LOCK = Lock() # éviter les races conditions
_ball_queue: deque[np.ndarray] = deque(maxlen=2 * LOOKBACK_FRAMES + 1) # +1 pour avoir au moins une position même si on n'a pas encore 0.2s de données

_last_update = 0.0


def get_ball_queue(client: rsk.Client) -> deque[np.ndarray]:
    global _last_update
    current_time = time.time()
    if current_time - _last_update >= QUEUE_UPDATE_PERIOD:
        _last_update = current_time
        if client.ball is not None:
            with QUEUE_LOCK:
                _ball_queue.append(client.ball)
    return _ball_queue


def get_future_ball_position(client: rsk.Client, prediction_time: float = QUEUE_UPDATE_PERIOD) -> np.ndarray | None:
    position_queue = get_ball_queue(client)
    with QUEUE_LOCK:
        if len(position_queue) < LOOKBACK_FRAMES + 1:
            return None # pas assez de données pour faire une prédiction

        # 1. Current Velocity (Compare now to 6 updates ago)
        current_velocity = (position_queue[-1] - position_queue[-1 - LOOKBACK_FRAMES]) / LOOKBACK_TIME
        
        # 2. Acceleration (Compare current velocity window to the previous window)
        acceleration = np.array([0.0, 0.0])
        if len(position_queue) >= (LOOKBACK_FRAMES * 2 + 1):
            previous_velocity = (position_queue[-1 - LOOKBACK_FRAMES] - position_queue[-1 - 2 * LOOKBACK_FRAMES]) / LOOKBACK_TIME
            acceleration = (current_velocity - previous_velocity) / LOOKBACK_TIME
            
            # Kick Detection: If direction change > 60 deg, ignore this acceleration spike
            if np.linalg.norm(current_velocity) > 0.05 and np.linalg.norm(previous_velocity) > 0.05:
                if get_angle_between(current_velocity, previous_velocity) > KICK_DETECTION_ANGLE_THRESHOLD:
                    acceleration = np.array([0.0, 0.0])      

        return position_queue[-1] + (current_velocity * prediction_time) + (0.5 * acceleration * (prediction_time**2))
    
    
def get_ball_velocity(client: rsk.Client) -> np.ndarray | None:
    position_queue = get_ball_queue(client)
    with QUEUE_LOCK:
        if len(position_queue) < LOOKBACK_FRAMES + 1:
            return None # pas assez de données pour faire une prédiction

        return (position_queue[-1] - position_queue[-1 - LOOKBACK_FRAMES]) / LOOKBACK_TIME