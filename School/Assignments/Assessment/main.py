# Imports
import pygame  # pygame is the primary library used for the simulation engine
import numpy as np  # this is for np's useful array features and maths
import random  # ensure randomised simulation on every run
import math  # additiona math functions
import sys  # for logging, debuggin
from noise import pnoise2  # map generation
import argparse  # parsing arguments


# General Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720  # sets up a 1280x720 display window
MAP_SIZE = 128  # how many pixels (blocks) the map will take up
FPS=60  # frames per second
TEXT_COLOUR = (255 ,255, 255)

## New and Improved Updated Constants
# Map
N_OBSTACLES = 30

AVOID_EDGE_MARGIN = 5
AVOID_EDGE_STRENGTH = 0.00007

# colours
BACKGROUND_FILL = (50,50,50)
CR_HOVER_COLOUR = (0, 255, 0)
# Camera
CA_SCROLL_SPEED = 25
CA_BORDER_MARGIN = 5

# Creature
CR_INITIAL_ENERGY = 100 # initial energy of a new creature (might change this into a output? who knows)
CR_ENERGY_DECAY = 0 # ts is energy lost per second

# Bg
B_NOISE_OCTAVE = 8 # noise octave for perlin noise gen
B_NOISE_SCALE = 4 # zoom of onise
B_WATER_THRESH = 130/255 # Water
B_SAND_THRESH = 120/255 # threshould for smth to be considered sand
B_COLFULEXP = 0.5 ## exponent to make shit more colourful
B_COLLESEXP = 1.1 ## exponent to make shit more duller (idk ts some wizard stuff tbh)
B_BORDER = 0.5 # darkerns the border by this much (reduces rgb by a factor of ts)
B_BORDERTHRESH = 8 # size of a tile in order for border to be drawn
B_DETECT = 2.5 # THIS IS VERY IMPORTANT ! THIS IS THE BEE DETECTION RADIUS OF EVERYTHING
B_SEP_THRESHOLD = 0.7
B_MAX_V = 0.1 # max velocit
B_MIN_V = 0.02

# hive constant
H_INITIAL_WORKERS = 20 # also number of drones
H_INITIAL_QUEENS = 1
H_BEE_COOLDOWN = 3 # number of frames before a bee can exit/enter
COMB_WIDTH, COMB_HEIGHT = 12, 9 # comb size in hive
EGG_CELL_VALUE = -2 # if a cell contains an egg

# FLOWERS
F_SIZE = 8 # unscaled

## INITIALISATION !!!
pygame.init()
pygame.font.init()
STATS_FONT = pygame.font.SysFont("Arial", 16)
# np.set_printoptions(threshold=sys.maxsize) # Make print np arrays more comprehensive

# 
# HELPER FUNCTIONS
#

def distance(pos1, pos2):
    return pos1.distance_to(pos2) 

def is_hovered(screen_width, screen_height, screen_pos):
    mouse = pygame.math.Vector2(pygame.mouse.get_pos())
    # this is a terrible (and long line of code). hover code.
    if (-screen_width < mouse.x - screen_pos.x <  screen_width) and (-screen_height < mouse.y - screen_pos.y < screen_height):
        return True
    else:
        return False

def gridpos2screen(x, camera_offset):
    """converts grid coords to screen coords"""
    # print(MAP_SIZE) # should be 128x128 by default
    return (x * sim.scaled - camera_offset)
    
def screenpos2grid(x, camera_offset):
    return ((x+camera_offset)/sim.scaled)

def hivepos2screen(x):
    # this is kinda stupid but i made hive 400x400 and not changeable but because im too lazy. maybe ill change it later
    # but at this point of time 27th april its not a big deal.
    # assuming 1280x720 display, hive is shown to be the last 400 pixels with a 10 pixecl offset
    # im going to make the hive 40x40 for arbitrary sake so each pos is 10
    return (pygame.Vector2(WINDOW_WIDTH-410, WINDOW_HEIGHT-410)+x*10)

def screenpos2hive(x):
    return ((x - pygame.Vector2(WINDOW_WIDTH-410, WINDOW_HEIGHT-410))/10)

def draw_text(surface, text, font, colour, position, anchor="topleft"):
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, position)
    surface.blit(text_surface, text_rect)


def get_sigmoid(x):
    return (1/(1+math.exp(-x)))

maparr = []

class Environment():
    def __init__(self, size, manager):
                # square.fill(col)
                # pixel_draw = pygame.Rect(5*(i+1), 5*(j+1), 15, 15)
                # screen.blit(square, pixel_draw)
        # print(np.mean(test))
        # pygame.draw.circle(screen, "black", (30, 30), 500)

        self.map_world_surface = pygame.Surface((size, size))
        self.generate_background_texture(size)

        self.cached_bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.cached_camera_offset = pygame.Vector2(-1,-1)
        self.cached_scaled = -1


    def generate_background_texture(self, size):
        x_offset = random.uniform(0,10000)
        y_offset = random.uniform(0,10000)
        # print("drawing background")
        self.maparr = np.zeros((size,size), dtype=float)
        self.map_col = np.empty((size, size), dtype=object)

        for i in range(len(self.maparr)):
            for j in range(len(self.maparr[i])):
                pno = pnoise2((i+x_offset)*B_NOISE_SCALE/size, (j+y_offset)*B_NOISE_SCALE/size, B_NOISE_OCTAVE)
                pno = (pno+1)/2
                self.maparr[i][j] = pno
                self.map_col[i][j] = self.get_tile_color(pno)

    def get_tile_color(self, pno):
        # converts perlin noise col to pno
        c = round(255 * (pno**1.1))
        fav = round(255 * (pno**0.5))

        if c/255 >= B_WATER_THRESH:
            col = (220-c, 200-(c/2), fav)
        elif B_SAND_THRESH < c/255 < B_WATER_THRESH:
            col = (fav, fav, c)
        else:
            col = (c,fav+15,c-10)

        return(col)

    def update_background(self, size, camera_offset, scaled_value):
        # print(self.maparr)
        # cache check
        if (camera_offset != self.cached_camera_offset or scaled_value != self.cached_scaled):
            self.actually_update_background(self.cached_bg, size, camera_offset, scaled_value)
            self.cached_camera_offset = camera_offset
            self.cached_scaled = scaled_value

        return self.cached_bg

    def actually_update_background(self, target_surface, size, camera_offset, scaled):
        target_surface.fill(BACKGROUND_FILL)

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
                # pno = self.maparr[i][j]
                col = self.map_col[i][j]

                s = B_BORDER
                border = (int(col[0]*s),int(col[1]*s), int(col[2]*s) )

                pos = pygame.Vector2(i, j)
                mouse = pygame.math.Vector2(pygame.mouse.get_pos())
                # print(camera_offset)
                pos_scaled = gridpos2screen(pos, camera_offset)
                
                # print(pos_scaled, mouse)
                
                # print(camera_offset)

                # print(scaled_x, scaled_y)

                # pygame.draw.rect(background_surface, col, (500, 500, 50, 50))
                pygame.draw.rect(target_surface, col, (pos_scaled.x, pos_scaled.y, scaled, scaled))

                if scaled > 8:
                    pygame.draw.rect(target_surface, border, (pos_scaled.x, pos_scaled.y, scaled, scaled), 1)

# 
# CLASSES
#

class Simulation():
    def __init__(self, initial_world_size=4096):
        #prev global variables
        self.scaled = initial_world_size/MAP_SIZE
        self.frames = 0

        self.number_of_bees = H_INITIAL_WORKERS
        self.initial_bee_energy = CR_INITIAL_ENERGY
        self.hive_release_cooldown = H_BEE_COOLDOWN
        self.number_obstacles = N_OBSTACLES

        self.creatures = []
        self.hives = []
        self.flowers = []
        self.selected_bee = None
        self.selected_hive = None
        self.camera_offset = pygame.Vector2(0,0)

        self.obstacles = []

        self.obstaclemap = np.zeros((MAP_SIZE+1, MAP_SIZE+1))

        self.background = None

    def update_values(self, number_of_bees, initial_bee_energy, hive_release_cooldown, number_obstacles):
        self.number_of_bees = number_of_bees
        self.initial_bee_energy = initial_bee_energy
        self.hive_release_cooldown = hive_release_cooldown
        self.number_obstacles = number_obstacles
        
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

    def spawn_new_bee(self, hive, spawn_pos):
        temp_bee = Creature(hive.pos.x, hive.pos.y, hive, self, "worker") # set this to queen for awesome exponential growth!

        self.add(temp_bee)
        hive.bees_inside.append(temp_bee)
        temp_bee.hive_pos = pygame.Vector2(spawn_pos)

    def add_obstacles(self, obstacle):
        self.obstacles.append(obstacle)
        center_x = int(obstacle.pos.x)
        center_y = int(obstacle.pos.y)
        size=obstacle.size
        for i in range(2*obstacle.size):
            pos_x = center_x - obstacle.size + i
            for j in range(2*obstacle.size):
                pos_y = center_y - obstacle.size + j
                # print(i,j, obstacle.size*2-1)
                if (i == 0 or i == 2*obstacle.size-1) or (j == 0 or j == 2*obstacle.size-1):
                    # print(pos_x, pos_y, obstacle.size, obstacle.pos)
                    self.obstaclemap[pos_x, pos_y] = 1
        # print(self.obstaclemap)

    def add_background(self, background):
        self.background = background

    def run(self):
        # increment curr frame by 1
        self.frames += 1

        for hive in self.hives[:]:
            hive.update(self)
        for bee in self.creatures[:]:
            bee.update(self)
        for flower in self.flowers[:]:
            flower.update(self)
        for obstacle in self.obstacles[:]: 
            obstacle.update(self)

        # for creature in self.creatures[:]:
        #     creature.update(self)
        self.show_selected()
        self.check_mouse_movement()

    def check_mouse_movement(self):
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

        self.camera_offset = self.camera_offset + mouse_offset

        # if scaled = world_size/map_size, world_size = scaled*map_size

        self.camera_offset.x = max(0, min(self.camera_offset.x, self.scaled * MAP_SIZE - WINDOW_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.scaled * MAP_SIZE - WINDOW_HEIGHT))

    
    def handle_click(self, click_pos_screen, camera_offset):
        clicked = False # by default it is not clicked

        click_vec = pygame.Vector2(click_pos_screen)

        self.selected_bee = None
        self.selected_hive = None
        
        if not clicked: # if they clicked on hive
            for hive in reversed(self.hives):
                screen_pos = gridpos2screen(hive.pos, camera_offset)
                diff = pygame.math.Vector2.magnitude(screen_pos-click_vec) # gets the distance from cursor and hive
                if diff <= hive.size/2:
                    self.selected_hive = hive
                    clicked = True
                    print("yo you clicked on le hive")

        if not clicked:
            for bee in reversed(self.creatures): # this is reversed so the last drawn (top most bee) is checked first in case a bee is on top of another bees
                screen_pos = gridpos2screen(bee.pos, camera_offset)
                diff = pygame.math.Vector2.magnitude(screen_pos - click_vec)
                if diff <= bee.radius:
                    self.selected_bee = bee
                    clicked = True # breaks out of the for loop

    def add_objs(self, maparr):
        invalid_coords = []

        for i in range(2):
            random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            while maparr[int(random_coord.x)][int(random_coord.y)] >= B_WATER_THRESH or random_coord in invalid_coords:
                random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            sim.add_hive(Hive(random_coord.x,random_coord.y, sim, self))
            invalid_coords.append(random_coord)

        for i in range(25):
            random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            while maparr[int(random_coord.x)][int(random_coord.y)] >= B_WATER_THRESH or random_coord in invalid_coords:
                random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            sim.add_flo(Flower(random_coord.x, random_coord.y))
            invalid_coords.append(random_coord)

        for i in range(self.number_obstacles):
            random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            while maparr[int(random_coord.x)][int(random_coord.y)] >= B_WATER_THRESH or random_coord in invalid_coords:
                random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            sim.add_obstacles(Obstacle(random_coord.x, random_coord.y))
            invalid_coords.append(random_coord)



    def show_selected(self):
        # Check if there is a selected bee
        if (not self.selected_bee) and (not self.selected_hive):
            return

        gui_pos = pygame.Vector2(10,10) 
        gui_width = 300
        gui_height = 200
        
        
        if (self.selected_bee):
            panel_surface = pygame.Surface((gui_width, gui_height), pygame.SRCALPHA) #src alpha is used for transparency
            panel_surface.fill((0,0,0,150)) # semi transparent
            screen.blit(panel_surface, (gui_pos))

            bee = self.selected_bee

            stats = {
                "Position": bee.pos,
                "Velocity": bee.velocity,
                "Energy": bee.energy,
                "Honey": bee.honey,
                "Seeking Honey?": bee.seeking_honey,
                "Closest Flower Position": (bee.closestflower.pos if bee.closestflower != None else "None"),
                "Colour": bee.colour,
                "Honey": bee.honey,
                "Total Honey Aquired": bee.total_honey,
                "Role": bee.role,
            }
            
            offset = 20
            for key, value in stats.items():
                if isinstance(value, pygame.Vector2):
                    display_value = f"({value.x:.2f}, {value.y:.2f})"
                elif isinstance(value, float):
                    display_value = f"{value:.2f}"
                else:
                    display_value = str(value)
                text = f"{key}: {display_value}"

                draw_text(screen, text, STATS_FONT, TEXT_COLOUR, (gui_pos.x, offset))
                offset+= 20
        elif (self.selected_hive):
            gui_width = 400
            gui_height = 400
            panel_surface = pygame.Surface((gui_width, gui_height), pygame.SRCALPHA)#src alpha is used for transparency
            panel_surface.fill((50,25,0,255)) # semi transparent
            screen.blit(panel_surface, ((WINDOW_WIDTH-gui_width - 10, WINDOW_HEIGHT-gui_height - 10)))
            
            bees_inside = self.selected_hive.bees_inside

            ## drawing the comb
            col = pygame.Color(0)
            i = 0 # counter
            for comb_center in self.selected_hive.combs:
                honey = self.selected_hive.combs_honey[math.floor(i/COMB_WIDTH), i % COMB_WIDTH]
                if honey >= 0: # does not draw invalid combs (-1)
                    # print(honey)
                    col.hsla =((20+40*honey/100, 100, 50*honey/100+15, 100))
                    h_pos = hivepos2screen(pygame.Vector2(comb_center))
                    pygame.draw.circle(screen, (col.r, col.g, col.b), h_pos, 10)
                if honey <=-2:
                    col.hsla =((92, 100, 50, 100))
                    h_pos = hivepos2screen(pygame.Vector2(comb_center))
                    pygame.draw.circle(screen, (col.r, col.g, col.b), h_pos, 10)
                i+=1

            for bee in self.selected_hive.bees_inside:
                bee.draw_inside_hive()



class Flower():
    def __init__(self,x,y):
        self.pos=pygame.Vector2(x,y)

        self.size = F_SIZE
        self.petalCol = (random.randint(100,255), 255, random.randint(100,255)) # ts does not do anything
        self.pollen = 100000

        self.n_bees = 0

        self.angle = 0 # initial angle
        self.rotspeed = 0.005 # rotational speed
    
    def update(self, manager):
        # self.angle += self.rotspeed
        self.draw(manager.camera_offset, manager.scaled)

        if self.pollen <= 0:
            manager.rem_flo(self)
            print("I BLEW UP!!!")

    def draw(self, camera_offset, scaled):
        screen_pos = gridpos2screen(self.pos, camera_offset)

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
        pygame.draw.circle(screen, self.petalCol, (screen_pos), scaled)
        draw_text(screen, f"{self.n_bees}", STATS_FONT, TEXT_COLOUR, (screen_pos))

class Node():
    def __init__(self, parent=None, position=None):
        self.parent=parent
        self.position=position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        self.position = other.position

class Obstacle():
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)

        self.size = random.randint(1,3) # i made it size of a flower because, why not!

        self.min_x = self.pos.x
        self.min_y = self.pos.y
        self.max_x = self.pos.x + self.size
        self.max_y = self.pos.y + self.size

    def update(self, manager):
        self.draw(manager.camera_offset, manager.scaled)

    def get_closest_point(self, obj_pos):
        closest_point = pygame.Vector2(0,0)

        closest_point.x = max(self.min_x, min(obj_pos.x, self.max_x))
        closest_point.y = max(self.min_y, min(obj_pos.y, self.max_y))

        return(closest_point)
        
    def draw(self, camera_offset, scaled):
        screen_pos = gridpos2screen(self.pos, camera_offset)
        
        pygame.draw.rect(screen, (80, 80, 80), (screen_pos.x, screen_pos.y, scaled*self.size, scaled*self.size))


class Hive():
    def __init__(self,x,y, sim, manager):
        self.pos=pygame.Vector2(x,y)

        self.workerspop = manager.number_of_bees
        self.dronespop = self.workerspop
        self.queenpop = H_INITIAL_QUEENS
        self.bees_inside = []
        self.bees_outside = []
        
        self.internal_cooldown = 0

        self.beelook = 0

        self.size = self.workerspop + self.queenpop
        # print(self.size)

        for i in range(self.workerspop):
            offset_pos = [((random.random()-0.5)*100), ((random.random()-0.5)*100)]
            temp_bee = Creature(x,y, self, manager, "worker")

            sim.add(temp_bee) # adds bee to the simulation since they are seeking it. once i add a hive view this will be edited
            self.bees_inside.append(temp_bee)

        for i in range(self.queenpop):
            offset_pos = [((random.random()-0.5)*100), ((random.random()-0.5)*100)]
            temp_bee = Creature(x,y, self, manager, "queen")

            sim.add(temp_bee) # adds bee to the simulation since they are seeking it. once i add a hive view this will be edited
            self.bees_inside.append(temp_bee)

        # for i in range(self.dronespop):
        #     offset_pos = [((random.random()-0.5)*100), ((random.random()-0.5)*100)]
        #     temp_bee = Creature(x,y, self, manager, "drone")
        #
        #     sim.add(temp_bee) # adds bee to the simulation since they are seeking it. once i add a hive view this will be edited
        #     self.bees_inside.append(temp_bee)

        self.combs = []
        self.combs_honey = np.zeros((9,12))
        radius = 1
        radius_long = radius/np.cos(np.pi/6)
        tringle_len = radius*np.tan(np.pi/6)

        # 25, 15 -> 50, 55 (diff of 25/100, 40/100)

        horizontal_diff = 2*radius
        for i in range(9):
            y_pos = (5 + i*(2*radius_long))
            if i % 2 == 0:
                offset_val = radius
            else:
                offset_val = 0
            # print(offset_val)
            for j in range(12):
                x_pos = 5 + j * (horizontal_diff) + offset_val
                self.combs.append((x_pos, y_pos))

                fake_comb_value = -1 # a value of -1 signifies the comb is unable to be used, and only used as a placeholder!!!

                # print(j,i)
                self.combs_honey[i, j] = 0 # init
                if ((j == 0) and (i - 3 <= 0)) or ((j==1) and (i-1 <= 0)):
                    self.combs_honey[i,j] = fake_comb_value
                if ((j==0) and (i+4) >= COMB_HEIGHT) or ((j==1) and (i+2 >= COMB_HEIGHT)):
                    self.combs_honey[i,j] = fake_comb_value
                if ((j == COMB_WIDTH-1) and (i-2 <= 0)) or ((j==COMB_WIDTH-2) and (i <= 0)):
                    self.combs_honey[i,j] = fake_comb_value
                if ((j== COMB_WIDTH-1) and (i+3) >= COMB_HEIGHT) or ((j== COMB_WIDTH-2) and (i+1 >= COMB_HEIGHT)):
                    self.combs_honey[i,j] = fake_comb_value


        print(self.combs_honey)

    def update(self, manager):
        # self.size = self.workerspop + self.queenpop
        # checks if it is selected
        if self.beelook >= len(self.bees_inside): # resets beelook (the poninter in array) if its past the length of arr
            self.beelook = 0


        if manager.frames % 60 == 1:
            self.update_eggs(manager)

        self.size = manager.scaled*4
        if self.internal_cooldown == 0 and len(self.bees_inside) > 0:
            # bee to look at variable

            # for every bee in inside
            # print(len(self.bees_inside), self.beelook)
            bee = self.bees_inside[self.beelook]
            if bee.seeking_honey == True:
                self.bees_inside.pop(self.beelook) # always pops the 0th bee 
                self.bees_outside.append(bee)
            else:
                self.beelook += 1
            self.internal_cooldown = manager.hive_release_cooldown
        elif self.internal_cooldown > 0 :
            self.internal_cooldown -= 1

        self.draw(manager.camera_offset)

    def update_eggs(self, manager):
        # print(self.combs_honey)
        a = 0
        b=0
        for i in self.combs_honey:
            for j in i:
                if j <= -2:
                    self.combs_honey[a, b%COMB_WIDTH] -= 1 # do this if you want the eggs to grow by themselves

                    if j <= -30: # amount of arbitrary relative growth to ""hatch""
                        self.combs_honey[a, b%COMB_WIDTH] = -1 # egg value
                        manager.spawn_new_bee(self, self.combs[b])
                b+=1
            a+=1


    def draw(self, camera_offset):
        screen_pos = gridpos2screen(self.pos, camera_offset)

        # draws the hive where its center is its coordinate self.pos (x,y)
        pygame.draw.rect(screen, (255, 255, 0), (screen_pos.x-self.size/2, screen_pos.y-self.size/2, self.size, self.size))

class Creature():
    def __init__(self, x, y, hive, manager, role):
        self.role = role

        self.pos = pygame.Vector2(x, y) #change pos later 
        
        self.energy = manager.initial_bee_energy

        self.honey = 0

        self.total_honey = 0

        self.angle = 0

        self.hive = hive

        self.hive_pos = (pygame.Vector2(random.randint(0,40), random.randint(0,40))) # to see if the function works. (it does!)

        # self.sensors = [[0, 5], [50, 7]]

        self.acceleration = pygame.Vector2(0,0)

        # self.acceleration = pygame.Vector2((random.random()-0.5)/100,(random.random()-0.5)/100)
        self.velocity = pygame.math.Vector2.rotate(pygame.Vector2(0.9, 0.9), random.randint(-360, 360))

        self.speed = pygame.math.Vector2.magnitude(self.velocity)
        # self.velocity = pygame.Vector2(0,0)

        self.colour = (random.randint(170,255), random.randint(170,255), random.randint(0,50))

        self.seeking_honey = True

        self.closestflower = None 

        self.eggs = 0 # all start off with 0 eggs, only queen bees are able to "produce" eggs

        self.size_raw = self.energy/500

        if self.role == 'worker':
            self.size_scaled = self.size_raw * manager.scaled
        if self.role == 'queen':
            self.size_scaled = self.size_raw * manager.scaled + 6
            self.seeking_honey = False
        else:
            self.size_scaled = self.size_raw * manager.scaled

        self.radius = (self.size_scaled+2)

        self.selectedframe = random.randint(0, 5) # this is used to give the bee a random frame of the 5 frames, to ensure that the bee has a different, more random cycle. 

        self.image_file = pygame.image.load('bee.png')

        # im not entirely sure if this actually does anything

    def update(self, manager):
        self.avoidedge(self.pos)
        # print("my current pos is: ", self.pos)

        """This (below) is unsed a_star_pathfind code. It doesnt effect physics or the simulation at all and purely visual. 
        It looks nice (and interesting!), but I have found little reason to use it on top of the bee's already complex behaviour. 
        This pathfinding *could* circumvent a very rare issue (that is the bee getting stuck between two rocks), 
        but since the map is too big and there is too little obstacles, i have decided not to use it.

        Moreover, it isnt really true to real life animal behaviour - animals rarely calculate the most "optimal" direction when heading towards an object, 
        as animals are incapable of storing the position of their target object and every obstacle in their path."""
        # if frames == 1:
        #     # get a non water pos
        #     random_pos = pygame.Vector2(random.randint(0,127), random.randint(0,127))
        #     while manager.background.maparr[int(random_pos.x), int(random_pos.y)] >= B_WATER_THRESH:
        #         random_pos = pygame.Vector2(random.randint(0,127), random.randint(0,127))
        #
        #     self.a_star_pathfind(manager, self.hive.pos, random_pos)
        is_worker = self.role == "worker" 
        is_outside = self in self.hive.bees_outside
        steering = pygame.Vector2(0,0)

        if is_worker:
            self.whatamidoing()

        if is_outside:
            # calculate forces every 5 frames
            if manager.frames % 5 == self.selectedframe:
                steering += self.calculateForces(self.hive.bees_outside, self.pos, manager) # calculates all the forces to do/adds

            steering += self.calculate_avoid_edge_force(self.pos, 0, MAP_SIZE) * 100
            steering += self.avoidrock(self.pos, manager)
            
            if is_worker:
                self.seekFlowers(manager.flowers)

            steering += self.avoidwater(manager.background.maparr) * 0.8
        elif not is_outside: # inside considered
            steering += self.calculate_avoid_edge_force(self.hive_pos, 0, 40) * 100

            if self in self.hive.bees_inside:
                self.avoidedge(self.hive_pos)
             
                steering += self.calculateForces(self.hive.bees_inside, (self.hive_pos), None)

                if self.seeking_honey == False or self.role == 'queen':
                    steering += self.dohoneythings() * 2.5 # function to fill up the honey

        if self.role == "queen":
            self.do_queen_things()

        if self.role == "drone":
            print("hullo i am a drone", is_outside, self.pos)


        self.applyForce(steering)
        self.velocity += self.acceleration
        self.acceleration *= 0 # reset acceleration

        
        fac = 30 # angle factor
        rotate = (random.random() - 0.5)*fac
        self.velocity = pygame.math.Vector2.rotate(self.velocity, rotate)
        
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        if self.speed >= B_MAX_V:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * B_MAX_V
        if 0 < self.speed <= B_MIN_V:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * B_MIN_V
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        if is_outside:
            self.pos += self.velocity
        else:
            self.hive_pos += self.velocity
        
        self.selected = (manager.selected_bee == self)

        if frames % FPS == 0: 
            self.energy = self.energy - CR_ENERGY_DECAY
            # print(self.energy)

        if self.energy <= 0:
            print("creature ran out of energy :(")
            if is_outside:
                self.hive.bees_outside.remove(self)
            else:
                self.hive.bees_inside.remove(self)
            manager.remove(self)

        self.size_raw = self.energy/500

        if self.role == 'worker':
            self.size_scaled = self.size_raw * manager.scaled
        if self.role == 'queen':
            self.size_scaled = self.size_raw * manager.scaled + 6
        else:
            self.size_scaled = self.size_raw * manager.scaled

        self.radius = (self.size_scaled+2)

        self.screen_pos = gridpos2screen(self.pos, manager.camera_offset)
        # despite its name real pos is actually the pos of the character on the monitor so real is all relative xdxd

        if is_outside:
            self.draw(manager.scaled)

    def applyForce(self, force):
        # print(force)
        self.acceleration += force / 15

    def whatamidoing(self):
        self.min_honey = 80

        if self.honey >= self.min_honey:
            self.seeking_honey = False

    def do_queen_things(self):
        """func to include all queen behaviours"""
        # 1. check eggs ready
        # 2. if eggs ready > 1 lay an egg
        # 3. egg will inhereit the genes of their parents (done later) 

        if frames % 60 == 0:
            self.eggs += 1

        if self.eggs > 1:
            pass    
        # lay egg

    def a_star_pathfind(self, manager, in_pos, target_pos):
        """note about this implementation:
        1. only works on grid (in this case MAP_SIZExMAP_SIZE which is 128x)
        2. i am schizophrenic so this might not wor
        3. this is based off random pseudocode i found in google images
        """
        print("we want to go from", in_pos, "to", target_pos)
        start_node=Node(None, in_pos)
        start_node.g = 0 
        start_node.h = distance(start_node.position, target_pos)
        start_node.f = start_node.g + start_node.h
        end_node=Node(None, target_pos)

        closed_list = [] # list of nodes that hasnt been searched
        open_list = [start_node] # the list of the nodes we have looked at

        while len(open_list) > 0 and len(closed_list) < 100: # when the list of open nodes is empty, which is unexpected, so it should return failure

            # print(len(closed_list), len(open_list))

            # getting the current node
            current_node = open_list[0] # for each current_node in the open current_node
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node.position == target_pos: # if we have reached the destination
                path = []
                curr = current_node

                while curr is not None:
                    path.append(curr.position)
                    curr = curr.parent

                for path_block in path:
                    manager.background.map_col[int(path_block.x), int(path_block.y)] = self.colour


                # print(path[::-1]) # return path but reversed
                return(path[::-1]) # return path but reversed

            # creating children
            # gets 3x3 grid around center

            children = []
            for i in range(-1,2): #i is x 
                for j in range(-1,2): # j is you
                    if (i == 0 and j == 0): # if centered
                        continue

                    node_pos = pygame.Vector2(current_node.position.x + i, current_node.position.y + j)
                    
                    if not (0 <= node_pos.x < MAP_SIZE and 0 <= node_pos.y < MAP_SIZE):
                        continue

                    if manager.background.maparr[int(node_pos.x), int(node_pos.y)] >= B_WATER_THRESH:
                        continue

                    if manager.obstaclemap[int(node_pos.x), int(node_pos.y)] == 1:
                        continue

                    child_node = Node(current_node, node_pos)
                    children.append(child_node)


            for child_node in children:
                in_closed = False

                for look_child in closed_list:
                    if child_node.position == look_child.position:
                        in_closed = True
                        break
                if in_closed == True:
                    continue

                child_node.g  = current_node.g + distance(current_node.position, child_node.position)
                child_node.h = distance(child_node.position, end_node.position)
                child_node.f = child_node.g + child_node.h

                in_open_list = False
                for open_node in open_list:
                    if child_node.position == open_node.position:
                        if child_node.g < open_node.g:
                            open_node.g = child_node.g
                            open_node.f = child_node.f
                            open_node.parent = current_node
                        in_open_list = True
                        break

                if in_open_list:
                    continue
                
                open_list.append(child_node)

        print("A* failed: we found no path :)")
        print(len(closed_list), len(open_list))
        return []
                        
        



    def seekFlowers(self, flowers):
        # 1. find closest flower
        # 2. if closest flower is arbitrarily ""close"" -> go to it
        # 3. if closest flower is ""far"" -> oh well! time to ''wander''
        # this code essentially does step (1)

        for flower in flowers:
            if not self.closestflower:
                self.closestflower = flower # sets the flower if it does not exist
                self.closestflower.n_bees += 1
            if distance(flower.pos, self.pos) < distance(self.pos, self.closestflower.pos) and flower.n_bees <= 10:
                # print(distance(flower.pos,self.pos))
                self.closestflower.n_bees -= 1
                self.closestflower = flower
                self.closestflower.n_bees += 1
                # print("CLOSEST FLOWER DETECTED!!", flower.pos)
        if self.seeking_honey == True:
            self.goFlower()
            if distance(self.pos, self.closestflower.pos) <= B_DETECT/4:
                self.honey += 0.5
                self.total_honey += 0.5
                self.closestflower.pollen -= 0.5
        elif self.seeking_honey == False: # If it is no longer seeking honey.
            self.goHive()
    
    def goFlower(self):
        # get vector from closest flower and itself
        # im not sure why but the current implementation the bees are circling the flowers
        if distance(self.pos, self.closestflower.pos) <= B_DETECT*3: 
            diffVec = + self.closestflower.pos - self.pos
            # normalise it, multiply by speed, and multplied by distance from flower
            outputVec = pygame.math.Vector2(diffVec) * self.speed * distance(self.closestflower.pos, self.pos)

            self.applyForce(outputVec)

    def goHive(self):
        hive_pos = self.hive.pos

        diffVec = hive_pos - self.pos
        # print((pygame.math.Vector2.magnitude(diffVec)))

        if (pygame.math.Vector2.magnitude(diffVec) <= 4):
            # print("enter hive")
            self.enter_hive()
        else:
            force_applied = pygame.math.Vector2.normalize(diffVec) * self.speed

            self.applyForce(force_applied)

    def enter_hive(self):
        self.hive.bees_inside.append(self)
        self.hive.bees_outside.remove(self)
#         # known error   File "/Users/thomas/Desktop/Code/School/Assignments/Assessment/main.py", line 686, in enter_hive
#     self.hive.bees_outside.remove(self)
# ValueError: list.remove(x): x not in list

    def calculateForces(self, bees, beepos, manager):
        """This Function Calculates the basic movement of the bees following the rules of boids"""
        # behaviours of bees: 
        # 1. flocking: boid behaviour with their 3 rules: 1. avoid other bees, 2. same speed as other bees, tend towards the center of a flock
        # 2. go to flowers
        # 3. random deviations in movement
        return (self.separation(bees, beepos) + self.align(bees, beepos) + self.cohesion(bees, beepos)) * 1.2

    def avoidrock(self, beepos, manager):
        # 1. logic to steer away from rock
        force = pygame.Vector2(0,0)
        if manager:
            for rock in manager.obstacles:
                closest_point = rock.get_closest_point(beepos)
                diff = beepos - closest_point
                diff_mag = pygame.math.Vector2.magnitude(diff)

                if (0 < diff_mag < B_SEP_THRESHOLD):
                    force += pygame.math.Vector2.normalize(diff) * (B_SEP_THRESHOLD-diff_mag)/(B_SEP_THRESHOLD)


        return force

    def avoidwater(self, maparr):
        force = pygame.Vector2(0,0)

        # print(maparr)
        if self.speed == 0 or maparr.all == None:
            return force
        
        direction = pygame.math.Vector2.normalize(self.velocity)
        look_pos = pygame.Vector2(0)
        look_pos.x = max(0, min(math.ceil(self.pos.x + direction.x), 127))
        look_pos.y = max(0, min(math.ceil(self.pos.y + direction.y), 127))
        # print(self.pos, look_pos)

        if (maparr[int(look_pos.x)][int(look_pos.y)]) >= B_WATER_THRESH:
            force -= direction

        return force

    
    def calculate_avoid_edge_force(self, beepos, min_bound, max_bound):
        force = pygame.Vector2(0,0)
        
        margin = AVOID_EDGE_MARGIN
        strength = AVOID_EDGE_STRENGTH

        if beepos.x <= min_bound+margin:
            force.x += strength * (-(beepos.x-min_bound) + margin) 
        elif beepos.x >= max_bound-margin:
            force.x -= strength * (margin + -(-beepos.x+max_bound)) 


        if beepos.y <= min_bound+margin:
            force.y+=strength * (margin + -(beepos.y-min_bound)) 

        elif beepos.y >= max_bound - margin:
            force.y-=strength * (margin + -(-beepos.y+max_bound)) 

        return force

    def avoidedge(self, beepos):
        if self in self.hive.bees_outside:
            self.pos.x = max(0, min(self.pos.x, 128))
            self.pos.y = max(0, min(self.pos.y, 128))
        else:
            self.hive_pos.x = max(0, min(self.hive_pos.x, 40))
            self.hive_pos.y = max(0, min(self.hive_pos.y, 40))

        # note to self: add bottom left right border  too! future note: done!

    def separation(self, bees, beepos):
        # The separation rule makes the boids avoid bumping into each other. This is done by calculating the distance between the current boid and all the other boids in the group. If the distance is less than a certain threshold, then the boid will move away from the other boid. This is done by calculating the vector from the current boid to the other boid. This vector is then normalized and multiplied by the speed of the boid. This is done in order to make sure that the boids do not move too fast.
        sepForce = pygame.Vector2(0,0)

        for bee in bees: 
            if beepos == self.hive_pos:
                detectpos = bee.hive_pos
            else: detectpos = beepos

            dist = distance(detectpos, beepos)

            if dist <= B_DETECT and detectpos != beepos:
                diffVec = detectpos - beepos
                # print(abs(distance(diffVec, beepos)))
                if abs(dist) <= B_SEP_THRESHOLD:
                    nomVec = pygame.Vector2.normalize(diffVec)
                    # print("Sep")

                    sepForce += nomVec/dist * self.speed * 2.5

        return(-sepForce)        


    # aligns the boid/bee to the average direction of its nearest "flock"
    def align(self, bees, beepos):
        avgV = pygame.Vector2(0,0)
        counter = 0

        for bee in bees: 
            if beepos == self.hive_pos:
                detectpos = bee.hive_pos
            else: detectpos = bee.pos

            dist = distance(detectpos, beepos)
            if 0 < dist <= B_DETECT and detectpos != beepos:
                avgV += bee.velocity
                counter += 1

        if counter != 0 and pygame.Vector2.magnitude(avgV) != 0:
            alignV = avgV/counter

            alignD = pygame.Vector2.normalize(alignV) * self.speed * 0.5 # 0.5 is arbitrary value to make the align force weaker

            # if self == bees.selected_bee:
            #     print(f"align dir {alignD}")

            return(alignD)
        
        return (avgV)

    # aims the bee towards to center of the ""flock""
    def cohesion(self, bees, beepos):
        com = pygame.Vector2(0,0) # center of mass
        counter = 0
        for bee in bees:
            if beepos == self.hive_pos:
                detectpos = bee.hive_pos
            else: detectpos = bee.pos

            dist = distance(detectpos, beepos)
            if 0 < dist <= B_DETECT and detectpos != beepos:
                counter += 1
                com += detectpos

        if counter != 0 and com != beepos: # makes sure magnitude of diff != 0
            com /= counter

            diff = com - beepos

            if pygame.math.Vector2.magnitude(diff) == 0:
                return (com) # i think this fixes the error below im not sure
                print("special return when diff = 0")

            dir = pygame.Vector2.normalize(diff) * self.speed
            ## known bug:     dir = pygame.Vector2.normalize(diff) * self.speed
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ValueError: Can't normalize Vector of length zero

            # print("applying force of, ", dir)
            return(dir)
        return (com)
        
    def draw(self, scaled):
        ## actually drawing the creatures
        # print(camera_offset)
        # if scaled > 8:
        #     screen.blit(self.image_file, self.screen_pos)
        pygame.draw.circle(screen, self.colour, self.screen_pos, (self.size_scaled+3)) 
        if self.selected == True:
            pygame.draw.circle(screen, CR_HOVER_COLOUR, self.screen_pos, (self.size_scaled+4), 2) 
            pygame.draw.circle(screen, CR_HOVER_COLOUR, self.screen_pos, self.size_scaled+B_DETECT*scaled, 2) # Drawing Detect Radius
            # pygame.draw.circle(screen, CR_HOVER_COLOUR, self.screen_pos, self.size_scaled+B_DETECT*3*scaled, 2)
            pygame.draw.circle(screen, (255,0,0), self.screen_pos, self.size_scaled+B_SEP_THRESHOLD*scaled, 2) # Drawing avoid radius

        # drawing creature's ""eyes""
        # for i in self.sensors:
        #     angle = np.deg2rad(i[0])
        #     distance = i[1]
        #     distance_added = pygame.Vector2(distance*np.cos(angle), distance*np.sin(angle))
        #
        #
        #     pygame.draw.line(screen, (255, 0, 0), self.screen_pos, self.screen_pos +distance_added*scaled, width=2)

    def dohoneythings(self):
        # 1. search for all combs inside hive to find first comb with not max honey
        i = 0
        j = 0 # counter

        diff = pygame.Vector2(0,0)
        nomForce = pygame.Vector2(0,0)

        # check honey status
        if self.honey <= 0 and self.role == 'worker':
            print("im removing myself (from hive)")
            self.seeking_honey = True
            self.hive.bees_outside.append(self)
            self.hive.bees_inside.remove(self)

        comb_pos = None
        for comb_honey in self.hive.combs_honey:
            for comb_honey_actual in comb_honey:
                comb_pos = pygame.math.Vector2(self.hive.combs[i][0], self.hive.combs[i][1])
                lowest_egg = -1
                if self.role == 'worker':
                    if 0 <= comb_honey_actual <= 100: # if it is not max and if it is not invalid
                        diff = comb_pos - self.hive_pos
                        # print(comb_pos)
                        if pygame.math.Vector2.magnitude(diff) <= 1 and self.honey >= 0:
                            self.honey -= 0.1
                            self.hive.combs_honey[j, i%COMB_WIDTH] += 0.1
                elif self.role == 'queen':
                    if lowest_egg <= comb_honey_actual <= -1:
                        lowest_egg = comb_honey_actual
                        diff = comb_pos - self.hive_pos
                        # print("i wanna go here", comb_pos, comb_honey_actual)
                        if pygame.math.Vector2.magnitude(diff) <= 1 and self.eggs > 0:
                            self.eggs -= 1
                            self.hive.combs_honey[j, i%COMB_WIDTH] -= 1 # egg value
                i+=1
            j+=1
        # 2. dif fpos from self
        if comb_pos:
            if pygame.math.Vector2.magnitude(diff) != 0:
                nomForce = pygame.math.Vector2.normalize(diff) * self.speed
        return (nomForce)
            
    def draw_inside_hive(self):
        size = self.energy/20

        if self.role == "queen":
            size *= 2
            pygame.draw.circle(screen, (255, 0, 0), hivepos2screen(self.hive_pos), size+2, 2) 
        pygame.draw.circle(screen, self.colour, hivepos2screen(self.hive_pos), size) 



parser = argparse.ArgumentParser(description="Simulate Bees")

parser.add_argument('-i', '--interactive', action='store_true', help='interactive mode')

args = parser.parse_args()

sim = Simulation()

if args.interactive:
    try:
        print("::::::::::::::::::::::INPUTS::[Interactive Mode]::::::::::::::::::::::")
        number_of_bees = int(x) if (x := input(f"Number of bees per hive (default={H_INITIAL_WORKERS}): ")) else H_INITIAL_WORKERS
        initial_bee_energy = int(x) if (x := input(f"Bee Initial Energy (default={CR_INITIAL_ENERGY}): ")) else CR_INITIAL_ENERGY
        hive_release_cooldown = int(x) if (x := input(f"Hive Bee Release Cooldown (default={H_BEE_COOLDOWN} frames): ")) else CR_INITIAL_ENERGY
        number_obstacles = int(x) if (x := input(f"Number of obstacles (default={N_OBSTACLES}): ")) else N_OBSTACLES
        sim.update_values(number_of_bees, initial_bee_energy, hive_release_cooldown, number_obstacles)
        print("::::::::::::::::::::::[End Interactive Mode]::::::::::::::::::::::")
    except:
        print("Input Error: Check your inputs and try again")
frames = 0
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.event.set_grab(True)

mouse = pygame.Vector2(0,0)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill(BACKGROUND_FILL)
screen.fill("white")

background = Environment(MAP_SIZE, sim)
sim.add_background(background)

sim.add_objs(background.maparr)

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    sim.handle_click(event.pos, sim.camera_offset)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    # print("awesome")
                    temp_world_size = min(sim.scaled*MAP_SIZE * 2, 16384)
                    sim.scaled = temp_world_size/MAP_SIZE
                    background.cached_scaled = -1
                if event.key == pygame.K_MINUS:
                    temp_world_size = max(512, sim.scaled*MAP_SIZE / 2)
                    sim.scaled = temp_world_size/MAP_SIZE
                    background.cached_scaled = -1
        
        screen.fill(BACKGROUND_FILL)
        
        current_background_view = background.update_background(MAP_SIZE, sim.camera_offset, sim.scaled)

        screen.blit(current_background_view, (0,0))
        # background_surface.fill(BACKGROUND_FILL)
        # background.update_background(MAP_SIZE, sim.camera_offset)

        # test_area = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        # screen.blit(background_surface, (0,0), area=test_area)
        # pygame.draw.circle(screen, "black", (30, 30), 500)

        sim.run()

        pygame.display.flip()
        clock.tick(FPS)
        pygame.display.set_caption(f"simulation | {round(clock.get_fps(), 2)} fps")
    

    pygame.quit()

if __name__ == "__main__":
    main()
