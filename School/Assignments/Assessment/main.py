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
mouse = pygame.Vector2(0,0)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill((50,50,50))


class Simulation():
    def __init__(self):
        self.creatures = []

    def add(self,creature):
        self.creatures.append(creature)

    def remove(self,creature):
        self.creatures.remove(creature)

    def run(self):
        for creature in self.creatures[:]:
            creature.update(self)

class Creature():
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y) #change pos later 
        
        self.energy = 100

        self.sensors = [[0, 5], [50, 7]]


        # Potential Inputs:
        # Energy
        # Velocity

        # Outputs
        # Acceleration

    def update(self, manager):
        global mouse

        if frames % 60 == 0: 
            self.energy = self.energy - 1
            print(self.energy)

        if self.energy <= 90:
            manager.remove(self)

        self.size_raw = self.energy/500

        self.scaled = WORLD_SIZE/MAP_SIZE
        self.size_scaled = self.size_raw * self.scaled*2

        self.screen_pos = pygame.Vector2(self.pos.x*self.scaled-camera_offset.x, self.pos.y *self.scaled - camera_offset.y) # despite its name real pos is actually the pos of the character on the monitor so real is all relative xdxd

        self.col = (0,0,0)

        if (self.screen_pos.x - self.size_scaled < mouse.x < self.screen_pos.x + self.size_scaled) and (self.screen_pos.y - self.size_scaled < mouse.y < self.screen_pos.y + self.size_scaled):
            self.col = (0,255,0)

        self.draw()

    def draw(self):
        
        ## actually drawing the creatures
        # print(camera_offset)
        pygame.draw.circle(screen, self.col, self.screen_pos, self.size_scaled, int(self.scaled/8))

        # drawing creature's ""eyes""
        for i in self.sensors:
            angle = np.deg2rad(i[0])
            distance = i[1]
            distance_added = pygame.Vector2(distance*np.cos(angle), distance*np.sin(angle))
            

            pygame.draw.line(screen, (255, 0, 0), self.screen_pos, self.screen_pos +distance_added*self.scaled, width=2)




sim = Simulation()
test_guy = Creature(5, 4.5)
sim.add(test_guy)

def check_mouse_movement():
    global camera_offset
    global mouse
    
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
        # pygame.draw.circle(screen, "black", (30, 30), 500)

        sim.run()



        pygame.display.flip()
        clock.tick(60)
    

    pygame.quit()

if __name__ == "__main__":
    main()
