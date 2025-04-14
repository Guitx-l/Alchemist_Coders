import pygame
from pygame import Vector2
import numpy as np
import math
pygame.init()
pygame.display.init()

fps = 60
fpsClock = pygame.time.Clock()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
font = pygame.font.SysFont("Arial", 12)
mouse_pos = Vector2(80, 240)
is_open = True
white = pygame.Color('white')
red = pygame.Color('red')
blue = pygame.Color('blue')
green = pygame.Color('green')
goal_pos = Vector2(640, 240)
middle = Vector2(320, 240)
rect_surface = pygame.Surface((20, 20))
rect_surface.fill(white)
circle_center: Vector2 = Vector2(320, 240)

def get_shoot_pos(goal_pos, ball_pos, shooter_offset_scale: float = 1) -> tuple[float, float, float]:
    #finding the shooter pos
    ball_to_goal_vector = goal_pos - ball_pos
    shooter_pos = ball_to_goal_vector * -shooter_offset_scale + goal_pos
    return shooter_pos[0], shooter_pos[1], math.atan2(ball_to_goal_vector[1], ball_to_goal_vector[0])

def in_circle(linepoint1: Vector2, linepoint2: Vector2, center: Vector2, radius: float) -> bool:
    line_vector = linepoint2 - linepoint1
    t = (center - linepoint1).dot(line_vector) / line_vector.length_squared()
    t = max(0., min(t, 1))
    return (Vector2(linepoint1.x + line_vector.x * t, linepoint1.y + line_vector.y * t) - center).length() <= radius

# Game loop.
while is_open:
    # Update.
    shoot_pos = get_shoot_pos(mouse_pos, middle)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        circle_center.y -= 4
    if keys[pygame.K_q]:
        circle_center.x -= 4
    if keys[pygame.K_s]:
        circle_center.y += 4
    if keys[pygame.K_d]:
        circle_center.x += 4

    # Draw.
    pygame.draw.circle(screen, red, middle, 240, width=4)
    pygame.draw.circle(screen, pygame.Color("yellow"), circle_center, 30, width=2)
    pygame.draw.aaline(screen, white, mouse_pos, middle)
    pygame.draw.line(screen, white, middle - (240, 0), middle + (240, 0))
    pygame.draw.line(screen, white, middle - (0, 240), middle + (0, 240))
    pygame.draw.line(screen, blue, mouse_pos, (mouse_pos.x, 240))
    pygame.draw.line(screen, green, mouse_pos, (320, mouse_pos.y))
    #pygame.draw.arc(screen, white, (middle - (50, 50), (100, 100)), 0, -shoot_pos[2], width=3)

    screen.blit(font.render(f"shooter position: {round(shoot_pos[0]), round(shoot_pos[1])}", True, white), (0, 0))
    screen.blit(font.render(f"dot to right line: {Vector2(*(mouse_pos - middle)).normalize().dot(Vector2(1, 0))}", True, white), (0, 12))
    screen.blit(font.render(f"angle: {round(math.degrees(shoot_pos[2]))}", True, white), (0, 24))
    screen.blit(font.render(f"line in circle: {in_circle(middle, mouse_pos, circle_center, 30)}", True, white), (0, 36))
    pygame.display.flip()
    fpsClock.tick(fps)

    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            is_open = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_vector = Vector2(*(event.pos - middle))
            try: mouse_pos = mouse_vector.normalize() * 240 + middle
            except ValueError: mouse_pos = middle



