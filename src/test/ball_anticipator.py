import rsk
import logging
import pygame
import numpy as np
from collections import deque
from pygame import Vector2

pygame.init()

# --- CONFIGURATION ---
FPS = 30 # We poll and predict at 30Hz
fpsClock = pygame.time.Clock()

SYSTEM_LATENCY = 0.1   # The base lag (e.g., 100ms)
SPEED_SENSITIVITY = 0.1 # How much extra lead per m/s
MAX_LEAD = 0.8         # Cap the prediction so it doesn't look off-field

# Physics Window: 0.2s baseline / (1/30s) = 6 frames lookback
LOOKBACK = 6 
# Total queue size needs to be double the lookback to calculate acceleration
position_queue = deque(maxlen=LOOKBACK * 2 + 1)

FONT = pygame.font.Font(None, 24)
width, height = 640, 480
screen = pygame.display.set_mode((width, height))

# Field Setup (RSK standard)
MIDDLE = Vector2(width / 2, height / 2)
COURT_SIZE = Vector2(width * 0.8, (rsk.constants.field_width / rsk.constants.field_length) * (width * 0.8))
SCALING_MATRIX = np.array([
    [COURT_SIZE.x / rsk.constants.field_length, 0], 
    [0, -COURT_SIZE.y / rsk.constants.field_width]
])
COURT_TOPLEFT = MIDDLE - COURT_SIZE / 2

# Colors
RED, GREEN, BLUE, WHITE = (255, 0, 0), (0, 255, 0), (0, 100, 255), (255, 255, 255)

def abs_coords(coords: Vector2) -> Vector2:
    return Vector2(tuple(np.array([coords.x, coords.y]) @ SCALING_MATRIX + COURT_TOPLEFT + 0.5 * COURT_SIZE))

def get_sliding_physics(queue: deque[Vector2]) -> tuple[Vector2, Vector2]:
    """Calculates v and a using a fixed 0.2s (6 frame) lookback."""
    if len(queue) < LOOKBACK + 1:
        return Vector2(), Vector2()

    # 1. Current Velocity (Compare now to 6 frames ago)
    # dt is exactly 0.2 seconds (6 * 1/30)
    dt = LOOKBACK / FPS
    current_velocity = (queue[-1] - queue[-1 - LOOKBACK]) / dt
    
    # 2. Acceleration (Compare current velocity window to the previous window)
    acceleration = Vector2(0, 0)
    if len(queue) >= (LOOKBACK * 2 + 1):
        previous_velocity = (queue[-1 - LOOKBACK] - queue[-1 - 2*LOOKBACK]) / dt
        acceleration = (current_velocity - previous_velocity) / dt
        
        # Kick Detection: If direction change > 60 deg, ignore this acceleration spike
        if current_velocity.length() > 0.05 and previous_velocity.length() > 0.05:
            if abs(current_velocity.angle_to(previous_velocity)) > 60:
                logging.info("kicking idk")
                acceleration = Vector2(0, 0)
                
    return current_velocity, acceleration

def get_dynamic_dt(velocity: Vector2, acceleration: Vector2) -> float:
    speed = velocity.length()
    accel = acceleration.length()
    
    # Simple linear scaling: 
    # More speed = More look-ahead
    dynamic_dt = SYSTEM_LATENCY + (speed * SPEED_SENSITIVITY)
    
    # Clamp the value so it stays realistic
    return min(dynamic_dt, MAX_LEAD)

with rsk.Client() as client:     
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                break

        # --- 1. POLL & UPDATE (30Hz) ---
        # We push to the queue every single loop iteration
        if client.ball is not None:
            ball_vector = Vector2(client.ball[0], client.ball[1])
            position_queue.append(ball_vector)

        # --- 2. PHYSICS & PREDICTION ---
        velocity, acceleration = get_sliding_physics(position_queue)
        
        # Estimate position for the NEXT frame (1/30s ahead)
        dt_frame = get_dynamic_dt(velocity, acceleration)
        if len(position_queue) > 0:
            # Standard kinematic: x_f = x + vt + 0.5at^2
            future_pos = position_queue[-1] + (velocity * dt_frame) + (0.5 * acceleration * (dt_frame**2))
        else:
            future_pos = Vector2(0,0)

        # --- 3. DRAWING ---
        screen.fill((20, 20, 20))
        pygame.draw.rect(screen, WHITE, (*COURT_TOPLEFT, *COURT_SIZE), width=2)

        if len(position_queue) >= 2:
            # Draw History
            history_pixels = [abs_coords(p) for p in position_queue]
            pygame.draw.lines(screen, GREEN, False, history_pixels, width=1)

            # Draw Current Ball (White)
            pygame.draw.circle(screen, WHITE, abs_coords(position_queue[-1]), 8)

            # Draw Prediction (Blue)
            pred_pixels = abs_coords(future_pos)
            pygame.draw.circle(screen, BLUE, (int(pred_pixels.x), int(pred_pixels.y)), 10, width=2)
            pygame.draw.line(screen, BLUE, abs_coords(position_queue[-1]), pred_pixels, 1)

            # UI Text
            speed_text = FONT.render(f"Speed: {velocity.length():.2f} m/s", True, WHITE)
            screen.blit(speed_text, (20, 20))

        pygame.display.flip()
        fpsClock.tick(FPS)