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
FPS=60

## New and Improved Updated Constants
# Map
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
INITIAL_WORLD_SIZE = 4096
MAP_SIZE = 128

# colours
BACKGROUND_FILL = (50,50,50)
CR_HOVER_COLOUR = (0, 255, 0)
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
B_DETECT = 2 # THIS IS VERY IMPORTANT ! THIS IS THE BEE DETECTION RADIUS OF EVERYTHING
B_SEP_THRESHOLD = 1# IMPORTANT FOR SEPARATION. this is the min distance a boid/bee wants to be from another bee
B_MAX_V = 0.1 # max velocit
B_MIN_V = 0.02

# hive constant
H_INITIAL_WORKERS = 50
H_INITIAL_QUEENS = 1
H_BEE_COOLDOWN = 3 # number of frames before a bee can exit/enter

scaled = INITIAL_WORLD_SIZE/MAP_SIZE

# FLOWERS
F_SIZE = 8 # unscaled

# fonts
TEXT_COLOUR = (255 ,255, 255)

## INITIALISATION !!!
pygame.init()
pygame.font.init()
STATS_FONT = pygame.font.SysFont("Arial", 16)
# np.set_printoptions(threshold=sys.maxsize) # Make print np arrays more comprehensive

# 
# HELPER FUNCTIONS
#

def distance(pos1, pos2):
    posdif = pos2 - pos1
    return (abs(pygame.Vector2.magnitude(posdif)))

def is_hovered(screen_width, screen_height, screen_pos):
    mouse = pygame.math.Vector2(pygame.mouse.get_pos())
    # this is a terrible (and long line of code). hover code.
    if (-screen_width < mouse.x - screen_pos.x <  screen_width) and (-screen_height < mouse.y - screen_pos.y < screen_height):
        return True
    else:
        return False

def gridpos2screen(x):
    # print(MAP_SIZE) # should be 128x128 by default
    return (x * scaled - camera_offset)
    
def screenpos2grid(x):
    return ((x+camera_offset)/scaled)

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
    for i in range(len(maparr)):
        for j in range(len(maparr[i])):
            pno = pnoise2((i+x_offset)*B_NOISE_SCALE/size, (j+y_offset)*B_NOISE_SCALE/size, B_NOISE_OCTAVE)
            pno = (pno+1)/2
            maparr[i][j] = pno
            test.append(maparr[i][j])

    update_background(size)
            # square.fill(col)
            # pixel_draw = pygame.Rect(5*(i+1), 5*(j+1), 15, 15)
            # screen.blit(square, pixel_draw)
    # print(np.mean(test))
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


            if c/255 >= B_WATER_THRESH:
                col = (255-c, 255-c, fav)
            elif B_SAND_THRESH < c/255 < B_WATER_THRESH:
                col = (fav, fav, c)
            else:
                col = (c,fav,c)
            

            s = B_BORDER
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

# 
# CLASSES
#

class Simulation():
    def __init__(self):
        self.creatures = []
        self.hives = []
        self.flowers = []
        self.selected_bee = None
        self.selected_hive = None
        
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
        for hive in self.hives[:]:
            hive.update(self)
            for bee in hive.bees_outside:
                bee.update(self)
        for flower in self.flowers[:]:
            flower.update(self)
        # for creature in self.creatures[:]:
        #     creature.update(self)
        self.show_selected()
    
    def handle_click(self, click_pos_screen):
        clicked = False # by default it is not clicked

        click_vec = pygame.Vector2(click_pos_screen)

        self.selected_bee = None
        self.selected_hive = None

        if not clicked:
            for bee in reversed(self.creatures): # this is reversed so the last drawn (top most bee) is checked first in case a bee is on top of another bees
                screen_pos = gridpos2screen(bee.pos)
                diff = pygame.math.Vector2.magnitude(screen_pos - click_vec)
                if diff <= bee.radius:
                    # print("omg clicked on bee")
                    self.selected_bee = bee
                    clicked = True # breaks out of the for loop

        if not clicked: # if they clicked on hive
            for hive in reversed(self.hives):
                screen_pos = gridpos2screen(hive.pos)
                diff = pygame.math.Vector2.magnitude(screen_pos-click_vec) # gets the distance from cursor and hive
                if diff <= hive.size/2:
                    self.selected_hive = hive
                    clicked = True
                    print("yo you clicked on le hive")


    def show_selected(self):
        # Check if there is a selected bee
        if (not self.selected_bee) and (not self.selected_hive):
            return

        gui_pos = pygame.Vector2(10,10) 
        gui_width = 300
        gui_height = 170
        
        
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
                "Closest Flower Position": bee.closestflowerpos,
                "Colour": bee.colour,
                "Honey": bee.honey,
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


            # print(self.selected_hive.combs_honey)

            # print(self.combs)
                
            col = pygame.Color(0)
            i = 0 # counter
            for comb_center in self.selected_hive.combs:
                # print(math.floor(i/10), i % 10 )
                honey = self.selected_hive.combs_honey[math.floor(i/10), i % 10]

                col.hsla =((20+40*honey/100, 100, 50*honey/100+15, 100))

                h_pos = hivepos2screen(pygame.Vector2(comb_center))
                # print(h_pos)
                pygame.draw.circle(screen, (col.r, col.g, col.b), h_pos, 10)

                i+=1


            for bee in bees_inside:
                bee.draw_inside_hive()


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
        pygame.draw.circle(screen, self.petalCol, (screen_pos), scaled)


class Hive():
    def __init__(self,x,y, sim):
        self.pos=pygame.Vector2(x,y)

        self.workerspop = H_INITIAL_WORKERS
        self.numbeesinside = self.workerspop
        self.queenpop = H_INITIAL_QUEENS
        self.bees_inside = []
        self.bees_outside = []

        

        self.internal_cooldown = 0

        self.beelook = 0

        self.size = self.workerspop + self.queenpop
        # print(self.size)

        for i in range(self.workerspop):
            offset_pos = [((random.random()-0.5)*100), ((random.random()-0.5)*100)]
            temp_bee = Creature(x,y, self)

            sim.add(temp_bee) # adds bee to the simulation since they are seeking it. once i add a hive view this will be edited
            self.bees_inside.append(temp_bee)

        self.combs = []
        self.combs_honey = np.zeros((10,10))
        radius = 1
        radius_long = radius/np.cos(np.pi/6)
        tringle_len = radius*np.tan(np.pi/6)

        # 25, 15 -> 50, 55 (diff of 25/100, 40/100)

        horizontal_diff = 2*radius
        for i in range(10):
            y_pos = (5 + i*(2*radius_long))
            if i % 2 == 0:
                offset_val = radius
            else:
                offset_val = 0
            # print(offset_val)
            for j in range(10):
                x_pos = 5 + j * (horizontal_diff) + offset_val
                self.combs.append((x_pos, y_pos))
                self.combs_honey[i, j] = random.randint(0,100) # init

        print(self.combs_honey)

    def update(self, manager):
        # self.size = self.workerspop + self.queenpop
        # checks if it is selected
        if self.beelook >= len(self.bees_inside): # resets beelook (the poninter in array) if its past the length of arr
            self.beelook = 0

        self.size = scaled*4
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
            self.internal_cooldown = H_BEE_COOLDOWN
        elif self.internal_cooldown > 0 :
            self.internal_cooldown -= 1

        self.draw()

    def draw(self):
        global mouse
        global scaled

        screen_pos = gridpos2screen(self.pos)

        # draws the hive where its center is its coordinate self.pos (x,y)
        pygame.draw.rect(screen, (255, 255, 0), (screen_pos.x-self.size/2, screen_pos.y-self.size/2, self.size, self.size))

class Creature():
    def __init__(self, x, y, hive):
        self.pos = pygame.Vector2(x, y) #change pos later 
        
        self.energy = CR_INITIAL_ENERGY

        self.honey = 0

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

        self.closestflowerpos = pygame.Vector2(999, 999)

        self.size_raw = self.energy/500

        self.size_scaled = self.size_raw * scaled

        self.radius = (self.size_scaled+2)

        self.selectedframe = random.randint(0, 5) # this is used to give the bee a random frame of the 5 frames, to ensure that the bee has a different, more random cycle. 
        # im not entirely sure if this actually does anything

    def update(self, manager):
        # global mouse
        # global scaled

        # print("my current pos is: ", self.pos)
        self.acceleration = pygame.Vector2(0,0) # reset acceleration
        
        self.whatamidoing()

        if frames % 5 == self.selectedframe:
            self.calculateForces(self.hive.bees_outside, self.pos) # calculates all the forces to do/adds

        # self.calculateForces(self.hive.bees_outside, self.pos) # calculates all the forces to do/adds

        self.seekFlowers(manager.flowers)

        # seeking flower code

        self.velocity += self.acceleration

        
        fac = 30 # angle factor
        rotate = (random.random() - 0.5)*fac
        self.velocity = pygame.math.Vector2.rotate(self.velocity, rotate)
        
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        if self.speed >= B_MAX_V:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * B_MAX_V
        if self.speed <= B_MIN_V:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * B_MIN_V
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        # print(self.velocity

        # map velocity + dampen
        # mapvalue = (1-(maparr[round(self.pos.x), round(self.pos.y)]))**(1/5)
        # if mapvalue >= 0.865: mapvalue = 0.99
        # self.velocity *= mapvalue**(1/5) # dampens

        self.pos += self.velocity
        
        # print(self.velocity, self.acceleration)

        self.selected = (manager.selected_bee == self)

        # if self.speed > max_speed:
        #     self.velocity.x = max_speed
        #     self.velocity.y = max_speed

        ## idk anymore

        if frames % FPS == 0: 
            self.energy = self.energy - CR_ENERGY_DECAY
            # print(self.energy)

        if self.energy <= 0:
            print("creature ran out of energy :(")
            self.hive.bees_outside.remove(self)
            manager.remove(self)

        self.size_raw = self.energy/500

        self.size_scaled = self.size_raw * scaled

        self.radius = (self.size_scaled+2)

        self.screen_pos = gridpos2screen(self.pos)
        # despite its name real pos is actually the pos of the character on the monitor so real is all relative xdxd


        self.draw()

    def applyForce(self, force):
        # print(force)
        self.acceleration += force / 15

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
                # print(distance(flower.pos,self.pos))
                self.closestflowerpos = flower.pos
                # print("CLOSEST FLOWER DETECTED!!", flower.pos)
        if self.seeking_honey == True:
            self.goFlower()
            if distance(self.pos, self.closestflowerpos) <= B_DETECT/4:
                self.honey += 0.5
        elif self.seeking_honey == False: # If it is no longer seeking honey.
            self.goHive()
    
    def goFlower(self):
        # get vector from closest flower and itself
        # im not sure why but the current implementation the bees are circling the flowers
        if distance(self.pos, self.closestflowerpos) <= B_DETECT*3: 
            diffVec = + self.closestflowerpos - self.pos
            # normalise it, multiply by speed, and multplied by distance from flower
            outputVec = pygame.math.Vector2(diffVec) * self.speed * distance(self.closestflowerpos, self.pos)

            self.applyForce(outputVec)

    def goHive(self):
        hive_pos = self.hive.pos

        diffVec = hive_pos - self.pos
        # print((pygame.math.Vector2.magnitude(diffVec)))

        if (pygame.math.Vector2.magnitude(diffVec) <= 4):
            print("enter hive")
            self.enter_hive()
        else:
            force_applied = pygame.math.Vector2.normalize(diffVec) * self.speed

            self.applyForce(force_applied)

    def enter_hive(self):
        self.hive.bees_inside.append(self)
        self.hive.bees_outside.remove(self)

    def calculateForces(self, bees, beepos):
        # behaviours of bees:
        # 1. flocking: boid behaviour with their 3 rules: 1. avoid other bees, 2. same speed as other bees, tend towards the center of a flock
        # 2. go to flowers
        # 3. random deviations in movement
        self.applyForce(self.separation(bees, beepos) + self.align(bees, beepos) + self.cohesion(bees, beepos) +self.avoidedge(beepos))

    def avoidedge(self, beepos):
        force = pygame.Vector2(0,0)

        if self in self.hive.bees_inside:
            real_hive_pos = (self.hive_pos)
            if real_hive_pos.x <= 1:
                force+=(pygame.Vector2(0.1, 0))
            elif real_hive_pos.x >= (39):
                force+=(pygame.Vector2(-0.1, 0))
            if real_hive_pos.y <= (1):
                force+=(pygame.Vector2(0, 0.1))
            elif real_hive_pos.y >= (39):
                force+=(pygame.Vector2(0, -0.1))
        else:
            if beepos.x <= 1:
                force+=(pygame.Vector2(0.1, 0) * abs(beepos.x -  5))
            elif beepos.x >= MAP_SIZE - 1:
                force+=(pygame.Vector2(-0.1, 0) * abs(beepos.x -  5))
            if beepos.y <= 1:
                force+=(pygame.Vector2(0, 0.1) * abs(beepos.y - 5))
            elif beepos.y >= MAP_SIZE - 1:
                force+=(pygame.Vector2(0, -0.1) * abs(beepos.y -  5))
        return(force)
        # note to self: add bottom left right border  too! future note: done!

    def separation(self, bees, beepos):
        # The separation rule makes the boids avoid bumping into each other. This is done by calculating the distance between the current boid and all the other boids in the group. If the distance is less than a certain threshold, then the boid will move away from the other boid. This is done by calculating the vector from the current boid to the other boid. This vector is then normalized and multiplied by the speed of the boid. This is done in order to make sure that the boids do not move too fast.
        sepForce = pygame.Vector2(0,0)

        for bee in bees: 
            if beepos == self.hive_pos:
                detectpos = bee.hive_pos
            else: detectpos = bee.pos

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
            if B_SEP_THRESHOLD < dist <= B_DETECT and detectpos != beepos:
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
            if B_SEP_THRESHOLD < dist <= B_DETECT and detectpos != beepos:
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
        
    def draw(self):
        ## actually drawing the creatures
        # print(camera_offset)
        pygame.draw.circle(screen, self.colour, self.screen_pos, (self.size_scaled+2)) 
        if self.selected == True:
            pygame.draw.circle(screen, CR_HOVER_COLOUR, self.screen_pos, (self.size_scaled+3), 2) 
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
        # 1. search for all combs inside hive
        for comb in self.hive.combs:
            print(comb)
        # 2. find location 

    def draw_inside_hive(self):
        # code on writing bee behaviour INSIDE the hive. i can tbe bothered so everything might be in this ONE function
        # self.hive_pos = (pygame.Vector2(random.randint(880, 1270), 650)) # temp screen pos inside hive
        # print(self.pos)
        # print(self.hive_pos)
        
        self.acceleration = pygame.Vector2(0,0) # reset acceleration
        
        self.calculateForces(self.hive.bees_inside, (self.hive_pos))

        self.dohoneythings() # function to fill up the honey

        self.velocity += self.acceleration
        
        fac = 30 # angle factor
        rotate = (random.random() - 0.5)*fac
        self.velocity = pygame.math.Vector2.rotate(self.velocity, rotate)
        
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        if self.speed >= B_MAX_V:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * B_MAX_V
        if self.speed <= B_MIN_V:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * B_MIN_V
        self.speed = pygame.math.Vector2.magnitude(self.velocity)
        # print(self.velocity

        # map velocity + dampen
        # mapvalue = (1-(maparr[round(self.pos.x), round(self.pos.y)]))**(1/5)
        # if mapvalue >= 0.865: mapvalue = 0.99
        # self.velocity *= mapvalue**(1/5) # dampens

        self.hive_pos += (self.velocity)

        pygame.draw.circle(screen, self.colour, hivepos2screen(self.hive_pos), (self.energy/20)) 
        # print("wow you are drawing me") # LOL



sim = Simulation()

sim.add_hive(Hive(10,10, sim))
sim.add_hive(Hive(100,100, sim))


for i in range(25):
    sim.add_flo(Flower(random.randint(10,118), random.randint(10,118)))


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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    sim.handle_click(event.pos)
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

        
        background_surface.fill(BACKGROUND_FILL)
        check_mouse_movement()
        update_background(MAP_SIZE)

        test_area = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill(BACKGROUND_FILL)
        screen.blit(background_surface, (0,0), area=test_area)
        # pygame.draw.circle(screen, "black", (30, 30), 500)

        sim.run()


        pygame.display.flip()
        clock.tick(FPS)
        pygame.display.set_caption(f"simulation | {round(clock.get_fps(), 2)} fps")
    

    pygame.quit()

if __name__ == "__main__":
    main()
