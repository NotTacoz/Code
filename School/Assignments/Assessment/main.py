import pygame
import numpy as np
import random
import math
import sys
from noise import pnoise2
np.set_printoptions(threshold=sys.maxsize)

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
square = pygame.Surface((15,15))

def get_sigmoid(x):
    return (1/(1+math.exp(-x)))


def draw_background(size):
    # print("drawing background")
    maparr = np.zeros((size,size), dtype=float)
    for i in range(len(maparr)):
        for j in range(len(maparr[i])):
            maparr[i][j] = pnoise2(i/size, j/size, 5)

            c = round(255 * ((maparr[i][j])+1)/2)
            if c < 150:
                c = 0

            print(c)
            
            col = (c,c,c)
            square.fill(col)
            pixel_draw = pygame.Rect(5*(i+1), 5*(j+1), 15, 15)
            screen.blit(square, pixel_draw)
            # pygame.draw.circle(screen, col, (i*2, j*2), 2)
    # pygame.draw.circle(screen, "black", (30, 30), 500)
    # print(maparr)

def main():
    screen.fill("white")
    draw_background(64)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

        # pygame.draw.circle(screen, "black", (30, 30), 500)

        pygame.display.flip()

        clock.tick(60)
    

    pygame.quit()

if __name__ == "__main__":
    main()
