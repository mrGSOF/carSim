import sys, pygame
from pygame.locals import *

pygame.init()
SCREEN = pygame.display.set_mode((200, 200))
CLOCK  = pygame.time.Clock()

surface = pygame.Surface((50 , 50), pygame.SRCALPHA)
surface.fill((0, 0, 0))
rotated_surface = surface
rect = surface.get_rect()
angle = 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    SCREEN.fill((255, 255, 255))
    angle += 5
    rotated_surface = pygame.transform.rotate(surface, angle)
    rect = (100, 100)
    rect = rotated_surface.get_rect(center = (100, 100))
    SCREEN.blit(rotated_surface, rect)

    pygame.display.update()
    CLOCK.tick(30)
    
