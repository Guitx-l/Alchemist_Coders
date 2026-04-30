import sys
import rsk
import time
import math
import pygame
import numpy as np
from collections import deque
from pygame import Vector2
 
pygame.init()
 
FPS = 60
fpsClock = pygame.time.Clock()
BALL_UPDATE_RATE = 1 # Hz
 
FONT = pygame.font.Font(None, 18)

width, height = 640, 480
screen = pygame.display.set_mode((width, height))

position_queue: deque[Vector2] = deque(maxlen=5)
ball_position = Vector2(0, 0)
last_timestamp = time.time()
MIDDLE = Vector2(width / 2, height / 2)

COURT_SIZE = Vector2()
COURT_SIZE.x = 0.9 * width
COURT_SIZE.y = rsk.constants.field_width / rsk.constants.field_length * COURT_SIZE.x
SCALING_MATRIX = np.array([
    [COURT_SIZE.x / rsk.constants.field_length, 0], 
    [0, -COURT_SIZE.y / rsk.constants.field_width]
    ])

COURT_TOPLEFT = MIDDLE - COURT_SIZE / 2

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)


def abs_coords(coords: np.ndarray | Vector2) -> Vector2:
    return coords @ SCALING_MATRIX + COURT_TOPLEFT + 0.5 * COURT_SIZE

def get_angle_between(v1: Vector2, v2: Vector2) -> float:
    return np.arccos(np.clip(v1.dot(v2) / (v1.length() * v2.length() + 0.0001), -1.0, 1.0))


def anticipate_ball_position(position_queue: deque) -> Vector2:
    if len(position_queue) == position_queue.maxlen:
        pass
    
    if len(position_queue) >= 2:
        # Fit a quadratic curve to the last few positions and extrapolate.
        times = np.arange(0, -5, -1) # Time steps for the last 3 positions.
        x_positions = np.array([pos.x for pos in position_queue])
        y_positions = np.array([pos.y for pos in position_queue])
        
        # Fit quadratic polynomials to x and y positions.

        coeffs_x = np.polyfit(times[:len(position_queue)], x_positions, 2)
        coeffs_y = np.polyfit(times[:len(position_queue)], y_positions, 2)
        
        # Extrapolate to the next time step (t=1).
        next_x = np.polyval(coeffs_x, 1)
        next_y = np.polyval(coeffs_y, 1)
        
        return Vector2(next_x, next_y)
    return position_queue[-1] if position_queue else Vector2(0, 0)

with rsk.Client() as client:     
    while True:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Update.
        if time.time() - last_timestamp > 1 / BALL_UPDATE_RATE and client.ball is not None:
            new_vector = Vector2(client.ball[0], client.ball[1])
            if len(position_queue) > 0 and get_angle_between(new_vector, position_queue[-1]) < math.radians(160):
                import icecream
                icecream.ic(math.degrees(get_angle_between(new_vector, position_queue[-1])))
                icecream.ic((new_vector - position_queue[-1]).length())
                position_queue.clear()

            position_queue.append(Vector2(client.ball[0], client.ball[1]))
            ball_position.x = client.ball[0]
            ball_position.y = client.ball[1]
            last_timestamp = time.time()
        # Draw.
        screen.fill((0, 0, 0))
        screen.blit(FONT.render(f"{math.degrees(get_angle_between(ball_position, Vector2(1, 0)))}", True, white), (10, 10))
        pygame.draw.rect(screen, white, (*COURT_TOPLEFT, *COURT_SIZE), width=2)
        try:
            pygame.draw.lines(screen, green, False, [abs_coords(pos) for pos in position_queue], width=2)
        except ValueError:
            pass
        pygame.draw.line(screen, red, abs_coords(anticipate_ball_position(position_queue)), abs_coords(ball_position))
        pygame.draw.circle(screen, white, abs_coords(ball_position), 10)
        
        
        pygame.display.flip()
        fpsClock.tick(FPS)