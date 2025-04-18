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
WORLD_SIZE = 1024

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.event.set_grab(True)

camera_offset = pygame.Vector2(500,500)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill((50,50,50))

camera_group = pygame.sprite.Group()

def check_mouse_movement():
    global camera_offset
    
    mouse = pygame.math.Vector2(pygame.mouse.get_pos())

    mouse_offset = pygame.Vector2(0,0)

    # # set up camera borders
    # left_border = self.camera_borders['left']
    # top_border = self.camera_borders['top'] 
    # right_border = self.display_surface.get_size()[0] - self.camera_borders['right']
    # bottom_border = self.display_surface.get_size()[1] - self.camera_borders['bottom']


    if mouse.y <= 0:
        mouse_offset.y = -5
    elif mouse.y >= WINDOW_HEIGHT - 1:
        mouse_offset.y = 5
    
    if mouse.x == 0:
        mouse_offset.x = -5
    elif mouse.x >= WINDOW_WIDTH - 1:
        mouse_offset.x = 5

    camera_offset += mouse_offset

def get_sigmoid(x):
    return (1/(1+math.exp(-x)))



def draw_background(size):
    test = []
    x_offset = random.uniform(0,10000)
    y_offset = random.uniform(0,10000)
    # print("drawing background")
    maparr = np.zeros((size,size), dtype=float)
    mult = 6
    scale = 8
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


def main():
    screen.fill("white")
    draw_background(128)

    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

        camera_offset.x = max(0, min(camera_offset.x, WORLD_SIZE - WINDOW_WIDTH))
        camera_offset.y = max(0, min(camera_offset.y, WORLD_SIZE - WINDOW_HEIGHT))
        
        check_mouse_movement()
        test_area = pygame.Rect(int(camera_offset.x), int(camera_offset.y), WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.blit(background_surface, (0,0), area=test_area)
        # pygame.draw.circle(screen, "black", (30, 30), 500)

        camera_group.update()

        pygame.display.flip()
        clock.tick(60)
    

    pygame.quit()

if __name__ == "__main__":
    main()
