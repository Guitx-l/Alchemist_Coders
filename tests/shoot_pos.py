import main_shooter
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
middle = np.array((320, 240))
rect_surface = pygame.Surface((20, 20))
rect_surface.fill(white)

# Game loop.
while is_open:
    # Update.
    shoot_pos = main_shooter.get_shoot_pos(np.array(mouse_pos), middle)

    pygame.draw.circle(screen, red, middle, 240, width=4)
    pygame.draw.aaline(screen, white, mouse_pos, middle)
    pygame.draw.line(screen, white, middle - (240, 0), middle + (240, 0))
    # Draw.
    surf = pygame.transform.rotate(rect_surface, -math.degrees(shoot_pos[2]))
    screen.blit(surf, surf.get_rect(center=middle))
    screen.blit(font.render(f"pos: {round(shoot_pos[0]), round(shoot_pos[1])}", True, white), (0, 0))
    screen.blit(font.render(f"dot: {-math.degrees(round(shoot_pos[2], 3))}", True, white), (0, 12))
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
            try: mouse_pos = mouse_vector.normalize() * 240 + middle
            except ValueError: mouse_pos = middle