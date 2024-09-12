import pygame
import sys
import time

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Arial", 30)
small = pygame.font.SysFont("Courier New", 15)
FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
SIZE = WIDTH, LENGTH = (900, 600)

screen = pygame.display.set_mode(SIZE, FLAGS)

if __name__ == "__main__":
    pygame.display.set_caption("Intercity Rail Game")
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
