import pygame
import numpy as np
import random
import math
import sys
from noise import pnoise2

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WORLD_SIZE = 4096
MAP_SIZE = 128

## New and Improved Updated Constants
# Map
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
INITIAL_WORLD_SIZE = 4096
MAP_SIZE = 128

# Colors
BACKGROUND_FILL = (50,50,50)
CR_HOVER_COLOR = (0, 255, 0)
SENSOR_COLOR = (255, 0, 0)

# Camera
CA_SCROLL_SPEED = 30
CA_BORDER_MARGIN = 5

# Creature
CR_INITIAL_ENERGY = 100 # initial energy of a new creature (might change this into a output? who knows)
CR_ENERGY_DECAY = 1 # ts is energy lost per second

# Bg
B_NOISE_OCTAVE = 8 # noise octave for perlin noise gen
B_NOISE_SCALE = 4 # zoom of onise
B_WATER_THRESH = 130/255 # Water
B_SAND_THRESH = 120/255 # threshould for smth to be considered sand
B_COLFULEXP = 0.5 ## exponent to make shit more colourful
B_COLLESEXP = 1.1 ## exponent to make shit more duller (idk ts some wizard stuff tbh)
B_BORDER = 0.5 # darkerns the border by this much (reduces rgb by a factor of ts)
B_BORDERTHRESH = 8 # size of a tile in order for border to be drawn
B_DETECT = 8 # THIS IS VERY IMPORTANT ! THIS IS THE BEE DETECTION RADIUS OF EVERYTHING

# hive constant
H_INITIAL_WORKERS = 10
H_INITIAL_QUEENS = 1

scaled = INITIAL_WORLD_SIZE/MAP_SIZE

# FLOWERS
F_SIZE = 8 # unscaled

## INITIALISATION !!!
pygame.init()
# np.set_printoptions(threshold=sys.maxsize) # Make print np arrays more comprehensive

 
class Simulation():
    def __init__(self):
        self.creatures = []
        self.hives = []
        self.flowers = []

    def add(self,creature):
        self.creatures.append(creature)

    def remove(self,creature):
        self.creatures.remove(creature)

    def add_hive(self, hive):
        self.hives.append(hive)

    def rem_hive(self, hive):
        self.hives.remove(hive)

    def add_flo(self, flower):
        self.flowers.append(flower)

    def rem_flo(self, flower):
        self.flowers.remove(flower)

    def run(self):
        for creature in self.creatures[:]:
            creature.update(self)
            creature.seekFlowers(self.flowers)
        for hive in self.hives[:]:
            hive.update(self)
        for flower in self.flowers[:]:
            flower.update(self)

class Flower():
    def __init__(self,x,y):
        self.pos=pygame.Vector2(x,y)

        self.size = F_SIZE
        self.petalCol = (random.randint(100,255), 255, random.randint(100,255))

        self.angle = 0 # initial angle
        self.rotspeed = 0.005 # rotational speed
    
    def update(self, manager):
        self.angle += self.rotspeed
        self.draw()

    def draw(self):
        screen_pos = gridpos2screen(self.pos)

        # petalCount = 6 # temp petalcount
        #
        # for i in range(petalCount):
        #     angle = i/petalCount * 2 * math.pi
        #
        #     offset_dist = scaled
        #
        #     offset_petal = pygame.Vector2(offset_dist * math.cos(angle), offset_dist*math.sin(angle))
        #
        #     draw_pos = screen_pos + offset_petal
        #
        #     pygame.draw.ellipse(screen, self.petalCol, (draw_pos.x, draw_pos.y, 0.5*scaled, 1.2*scaled))
        #
        pygame.draw.circle(screen, self.petalCol, (screen_pos), scaled/3)


class Hive():
    def __init__(self,x,y):
        self.pos=pygame.Vector2(x,y)

        self.workerspop = H_INITIAL_WORKERS
        self.queenpop = H_INITIAL_QUEENS

    def update(self, manager):
        self.size = self.workerspop + self.queenpop
        

        self.draw()

    def draw(self):
        global mouse
        global scaled

        screen_pos = gridpos2screen(self.pos)

        pygame.draw.rect(screen, (255, 255, 0), (screen_pos.x, screen_pos.y, self.size * scaled, self.size * scaled))

class Creature():
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y) #change pos later 
        
        self.energy = 100

        self.honey = 0

        self.angle = 0

        # self.sensors = [[0, 5], [50, 7]]

        self.velocity = pygame.Vector2((random.random()/5), (random.random()/5))

        self.acceleration = pygame.Vector2(0,0)

        self.color = (random.randint(170,255), random.randint(170,255), random.randint(0,50))

        self.seeking_honey = True

        self.closestflowerpos = pygame.Vector2(999, 999)

    def update(self, manager):
        global mouse
        global scaled

        max_speed = 5

        self.pos += self.velocity

        self.velocity += self.acceleration

        speed = pygame.math.Vector2.magnitude(self.velocity)
        if speed > max_speed:
            self.velocity = (5,5)

        self.acceleration = pygame.Vector2(0,0)

        self.whatamidoing()

        self.calculateForces(manager) # calculates all the forces to do/add

        # seeking flower code

        ## idk anymore

        if frames % 60 == 0: 
            self.energy = self.energy - 1
            # print(self.energy)

        if self.energy <= 0:
            print("creature ran out of energy :(")
            manager.remove(self)

        self.size_raw = self.energy/500

        self.size_scaled = self.size_raw * scaled*2

        self.screen_pos = gridpos2screen(self.pos)
        # despite its name real pos is actually the pos of the character on the monitor so real is all relative xdxd
        if (is_hovered(self.size_scaled, self.size_scaled, self.screen_pos)):
            self.color = (0,255,0)

        self.draw()

    def applyForce(self, force):
        self.acceleration = force

    def whatamidoing(self):
        self.min_honey = 80

        if self.honey >= self.min_honey:
            self.seeking_honey = False

    def seekFlowers(self, flowers):
        # 1. find closest flower
        # 2. if closest flower is arbitrarily ""close"" -> go to it
        # 3. if closest flower is ""far"" -> oh well! time to ''wander''
        # this code essentially does step (1)

        for flower in flowers:
            if distance(flower.pos, self.pos) < distance(self.pos, self.closestflowerpos):
                print(distance(flower.pos,self.pos))
                self.closestflowerpos = flower.pos
                # print("CLOSEST FLOWER DETECTED!!")
    
    def calculateForces(self, manager):
        # behaviours of bees:
        # 1. flocking: boid behaviour with their 3 rules: 1. avoid other bees, 2. same speed as other bees, tend towards the center of a flock
        # 2. go to flowers
        # 3. random deviations in movement
        self.separation(manager)

        self.align(manager)

        self.cohesion(manager)

    def separation(self, manager):
        for bee in manager.creatures:
            

    def align(self, manager):
        pass

    def cohesion(self, manager):
        pass
        
    
    def draw(self):
        ## actually drawing the creatures
        # print(camera_offset)
        pygame.draw.circle(screen, self.color, self.screen_pos, self.size_scaled, int(scaled/8))

        # drawing creature's ""eyes""
        # for i in self.sensors:
        #     angle = np.deg2rad(i[0])
        #     distance = i[1]
        #     distance_added = pygame.Vector2(distance*np.cos(angle), distance*np.sin(angle))
        #
        #
        #     pygame.draw.line(screen, (255, 0, 0), self.screen_pos, self.screen_pos +distance_added*scaled, width=2)



sim = Simulation()
test_guy = Creature(5, 4.5)
test_hive = Hive(10,10)
test_flower = Flower(2.5,2.5)
sim.add(test_guy)
# sim.add_hive(test_hive)
sim.add_flo(test_flower)

def distance(pos1, pos2):
    posdif = pos2 - pos1
    return (abs(pygame.Vector2.magnitude(posdif)))

def is_hovered(screen_width, screen_height, screen_pos):
    global mouse
    # this is a terrible (and long line of code). hover code.
    if (-screen_width < mouse.x - screen_pos.x <  screen_width) and (-screen_height < mouse.y - screen_pos.y < screen_height):
        return True
    else:
        return False

def gridpos2screen(x):
    global scaled, camera_offset
    # print(MAP_SIZE) # should be 128x128 by default
    return (x * scaled - camera_offset)
    
def screenpos2grid(x):
    global scaled, camera_offset
    return ((x+camera_offset)/scaled)

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
    for i in range(len(maparr)):
        for j in range(len(maparr[i])):
            pno = pnoise2((i+x_offset)*B_NOISE_SCALE/size, (j+y_offset)*B_NOISE_SCALE/size, 8)
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
    global scaled
    # print(maparr)
    start_col = math.floor(camera_offset.x / scaled)
    end_col = math.ceil((WINDOW_WIDTH + camera_offset.x) / scaled)
    start_row = math.floor((camera_offset.y) / scaled)
    end_row = math.ceil((camera_offset.y + WINDOW_HEIGHT) / scaled)

    #world bound
    start_col = max(0,start_col)
    end_col = min(size, end_col)
    start_row = max(0, start_row)
    end_row = min(size, end_row)

    # print(start_col, end_col, start_row, end_row)

    # print(math.ceil(WINDOW_HEIGHT/scaled))

    for i in range(start_col,end_col):
        for j in range(start_row, end_row):
            # print(i,j)
            # print(math.ceil(WINDOW_HEIGHT/scaled))
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
            pos_scaled = gridpos2screen(pos)
            
            # print(pos_scaled, mouse)
            
            # print(camera_offset)

            # print(scaled_x, scaled_y)

            # pygame.draw.rect(background_surface, col, (500, 500, 50, 50))
            pygame.draw.rect(background_surface, col, (pos_scaled.x, pos_scaled.y, scaled, scaled))

            if scaled > 8:
                pygame.draw.rect(background_surface, border, (pos_scaled.x, pos_scaled.y, scaled, scaled), 1)

frames = 0
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.event.set_grab(True)

camera_offset = pygame.Vector2(0,0)
mouse = pygame.Vector2(0,0)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill(BACKGROUND_FILL)
screen.fill("white")

def main():
    global scaled
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
                    scaled = WORLD_SIZE/MAP_SIZE
                if event.key == pygame.K_MINUS:
                    WORLD_SIZE = max(512, WORLD_SIZE / 2)
                    scaled = WORLD_SIZE/MAP_SIZE
        
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
