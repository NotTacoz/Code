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
    test = []
    x_offset = random.uniform(0,10000)
    y_offset = random.uniform(0,10000)
    # print("drawing background")
    maparr = np.zeros((size,size), dtype=float)
    mult = 6
    for i in range(len(maparr)):
        for j in range(len(maparr[i])):
            pno = pnoise2((i+x_offset)*mult/size, (j+y_offset)*mult/size, 50)
            pno = (pno+1)/2
            maparr[i][j] = pno
            test.append(maparr[i][j])

            c = round(255 * (pno**1.1))
            fav = round(255 * (pno**0.5))

            if c >= 130:
                col = (c-50, c-50, fav)
            elif 120 < c <= 129:
                col = (fav, fav, c)
            else:
                col = (c,fav,c)


            # print(col)
            
            square.fill(col)
            pixel_draw = pygame.Rect(5*(i+1), 5*(j+1), 15, 15)
            screen.blit(square, pixel_draw)
            # pygame.draw.circle(screen, col, (i*2, j*2), 2)
    print(np.mean(test))
    # pygame.draw.circle(screen, "black", (30, 30), 500)
    # print(maparr)

def main():
    screen.fill("white")
    draw_background(100)
    
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
