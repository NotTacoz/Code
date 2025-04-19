import pygame
import numpy as np
import random
import math
import sys
from noise import pnoise2


np.set_printoptions(threshold=sys.maxsize)

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WORLD_SIZE = 4096
MAP_SIZE = 128

pygame.init()
frames = 0
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.event.set_grab(True)

camera_offset = pygame.Vector2(0,0)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill((50,50,50))

class Creature():
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y) #change pos later 
        
        self.energy = 100

        # Potential Inputs:
        # Energy
        # Velocity

        # Outputs
        # Acceleration
    def draw(self):
        if frames % 60 == 0:
            self.energy = self.energy - 1
            # print(self.energy)
        self.size_raw = self.energy/500
        scaled = WORLD_SIZE/MAP_SIZE
        size_scaled = self.size_raw * scaled*2
        # print(camera_offset)
        pygame.draw.circle(screen, (0,0,0), (self.pos.x*scaled-camera_offset.x, self.pos.y*scaled-camera_offset.y), size_scaled)

test_guy = Creature(5, 4.5)

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
        mouse_offset.y = -25
    elif mouse.y >= WINDOW_HEIGHT - 1:
        mouse_offset.y = 25
    
    if mouse.x == 0:
        mouse_offset.x = -25
    elif mouse.x >= WINDOW_WIDTH - 1:
        mouse_offset.x = 25

    camera_offset += mouse_offset

def get_sigmoid(x):
    return (1/(1+math.exp(-x)))

maparr = []

def draw_background(size):
    test = []
    x_offset = random.uniform(0,10000)
    y_offset = random.uniform(0,10000)
    # print("drawing background")
    global maparr
    maparr = np.zeros((size,size), dtype=float)
    mult = 6
    scale = WORLD_SIZE/size
    for i in range(len(maparr)):
        for j in range(len(maparr[i])):
            pno = pnoise2((i+x_offset)*mult/size, (j+y_offset)*mult/size, 8)
            pno = (pno+1)/2
            maparr[i][j] = pno
            test.append(maparr[i][j])

    update_background(size)
            # square.fill(col)
            # pixel_draw = pygame.Rect(5*(i+1), 5*(j+1), 15, 15)
            # screen.blit(square, pixel_draw)
    print(np.mean(test))
    # pygame.draw.circle(screen, "black", (30, 30), 500)
    # print(maparr)

def update_background(size):
    scale = WORLD_SIZE/size
    # print(maparr)
    start_col = math.floor(camera_offset.x / scale)
    end_col = math.ceil((WINDOW_WIDTH + camera_offset.x) / scale)
    start_row = math.floor((camera_offset.y) / scale)
    end_row = math.ceil((camera_offset.y + WINDOW_HEIGHT) / scale)

    #world bound
    start_col = max(0,start_col)
    end_col = min(size, end_col)
    start_row = max(0, start_row)
    end_row = min(size, end_row)

    # print(start_col, end_col, start_row, end_row)

    # print(math.ceil(WINDOW_HEIGHT/scale))

    for i in range(start_col,end_col):
        for j in range(start_row, end_row):
            # print(i,j)
            # print(math.ceil(WINDOW_HEIGHT/scale))
            pno = maparr[i][j]
            c = round(255 * (pno**1.1))
            fav = round(255 * (pno**0.5))


            if c >= 130:
                col = (255-c, 255-c, fav)
            elif 120 < c <= 129:
                col = (fav, fav, c)
            else:
                col = (c,fav,c)
            

            s = 0.5
            border = (int(col[0]*s),int(col[1]*s), int(col[2]*s) )

            pos = pygame.Vector2(i, j)
            mouse = pygame.math.Vector2(pygame.mouse.get_pos())
            # print(camera_offset)
            pos_scaled = pos * scale - camera_offset

            # print(pos_scaled, mouse)
            
            # print(camera_offset)

            # print(scaled_x, scaled_y)
            

            # pygame.draw.rect(background_surface, col, (500, 500, 50, 50))
            pygame.draw.rect(background_surface, col, (pos_scaled.x, pos_scaled.y, scale, scale))

            if scale > 8:
                pygame.draw.rect(background_surface, border, (pos_scaled.x, pos_scaled.y, scale, scale), 1)

def main():
    screen.fill("white")

    draw_background(MAP_SIZE)
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN:
                global WORLD_SIZE
                if event.key == pygame.K_EQUALS:
                    # print("awesome")
                    WORLD_SIZE = min(WORLD_SIZE * 2, 16384)
                if event.key == pygame.K_MINUS:
                    WORLD_SIZE = max(512, WORLD_SIZE / 2)
        
        global frames
        frames += 1

        camera_offset.x = max(0, min(camera_offset.x, WORLD_SIZE - WINDOW_WIDTH))
        camera_offset.y = max(0, min(camera_offset.y, WORLD_SIZE - WINDOW_HEIGHT))



        
        background_surface.fill((50,50,50))
        check_mouse_movement()
        update_background(MAP_SIZE)

        test_area = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill((50,50,50))
        screen.blit(background_surface, (0,0), area=test_area)
        test_guy.draw()
        # pygame.draw.circle(screen, "black", (30, 30), 500)



        pygame.display.flip()
        clock.tick(60)
    

    pygame.quit()

if __name__ == "__main__":
    main()
