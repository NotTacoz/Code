import pygame
import numpy as np
import random
import math
import sys
from noise import pnoise2

# camera
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera setup
        self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottomm'])


        self.camera_rect = pygame.Rect(l,t,w,h)


np.set_printoptions(threshold=sys.maxsize)

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.event.set_grab(True)


background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill((50,50,50))

camera_group = pygame.sprite.Group()

def get_sigmoid(x):
    return (1/(1+math.exp(-x)))


def draw_background(size):
    test = []
    x_offset = random.uniform(0,10000)
    y_offset = random.uniform(0,10000)
    # print("drawing background")
    maparr = np.zeros((size,size), dtype=float)
    mult = 6
    scale = 6
    for i in range(len(maparr)):
        for j in range(len(maparr[i])):
            pno = pnoise2((i+x_offset)*mult/size, (j+y_offset)*mult/size, 8)
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
            pygame.draw.rect(background_surface, col, (i*scale, j*scale, scale, scale), 2)
    
            # square.fill(col)
            # pixel_draw = pygame.Rect(5*(i+1), 5*(j+1), 15, 15)
            # screen.blit(square, pixel_draw)
    print(np.mean(test))
    # pygame.draw.circle(screen, "black", (30, 30), 500)
    # print(maparr)

def mouse_control(self):
    mouse = pygame.math.Vector2(pygame.math.get_pos())
    mouse_offset_vector = pygame.math.Vector2()

    # set up camera borders
    left_border = self.camera_borders['left']
    top_border = self.camera_borders['top'] 
    right_border = self.display_surface.get_size()[0] - self.camera_borders['right']
    bottom_border = self.display_surface.get_size()[1] - self.camera_borders['bottom']

    # 
    if top_border < mouse.y < bottom_border:
        if mouse.x < left_border:
            mouse_offset_vector.x = mouse.x - left_border
            pygame.mouse.set_pos((left_border,mouse.y))

    self.offset += mouse_offset_vector

def main():
    screen.fill("white")
    draw_background(100)

    test_area = pygame.Rect(50, 50, 1280, 720)
    screen.blit(background_surface, (0,0), area=test_area)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

        # pygame.draw.circle(screen, "black", (30, 30), 500)

        camera_group.update()

        pygame.display.flip()
        clock.tick(60)
    

    pygame.quit()

if __name__ == "__main__":
    main()
