import attack
import pygame
import numpy as np
import math

pygame.init()
pygame.display.init()

fps = 60
fpsClock = pygame.time.Clock()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
font = pygame.font.SysFont("Arial", 12)
mouse_pos = np.array((80, 240))
is_open = True
white = pygame.Color('white')
red = pygame.Color('red')
goal_pos = np.array((640, 240))
middle = np.array((0, 240))

# Game loop.
while is_open:
    # Update.
    shoot_pos = attack.get_shoot_pos(middle, np.array(mouse_pos))
    pygame.draw.circle(screen, red, middle, 240, width=4)
    pygame.draw.aaline(screen, white, mouse_pos, middle)
    pygame.draw.line(screen, white, middle - (240, 0), middle + (240, 0))
    # Draw.
    screen.blit(font.render(f"pos: {round(shoot_pos[0]), round(shoot_pos[1])}", True, white), (0, 0))
    screen.blit(font.render(f"angle: {round(shoot_pos[2], 3)}", True, white), (0, 12))
    pygame.display.flip()
    fpsClock.tick(fps)

    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            is_open = False

        if event.type == pygame.MOUSEMOTION:
            mouse_vector = pygame.Vector2(*(event.pos - middle))
            mouse_pos = mouse_vector.normalize() * 240 + middle