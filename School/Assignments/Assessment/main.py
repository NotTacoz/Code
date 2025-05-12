"""
Bee Colony Simulation
===================

This program simulates a bee colony ecosystem with the following key components:
- Bees: Workers and queens that collect honey and maintain the hive
- Hives: Structures where bees live and store honey
- Flowers: Resources that bees collect honey from
- Environment: Generated terrain with water, land and obstacles

The simulation uses Pygame for visualization and implements flocking behavior
based on the Boids algorithm (separation, alignment, cohesion).

Key Features:
- Procedurally generated terrain using Perlin noise
- Realistic bee behavior with energy management
- Interactive visualization with zoom and pan controls
- Configurable simulation parameters
"""

# Standard library imports
import sys
import random
import math
import argparse
import time

# Third-party imports  
import pygame
import numpy as np
from noise import pnoise2
import csv

# Configuration Constants
# ---------------------

# Display settings
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720  # Window dimensions
MAP_SIZE = 128  # World grid size
FPS = 60  # Target frames per second
TEXT_COLOUR = (255, 255, 255)

# Map generation
N_OBSTACLES = 30  # Number of obstacles
AVOID_EDGE_MARGIN = 5  # Distance from edge to start avoidance
AVOID_EDGE_STRENGTH = 0.00007  # Force multiplier for edge avoidance

# Visual settings
BACKGROUND_FILL_COLOUR = (50, 50, 50)
CREATURE_HOVER_COLOUR = (0, 255, 0)

# Camera controls
CAMERA_SCROLL_SPEED = 25
CAMERA_BORDER_MARGIN = 5

# Creature properties
CREATURE_INITIAL_ENERGY = 50
CREATURE_ENERGY_DECAY_RATE = 1
CREATURE_DETECTION_RADIUS = 2.5
CREATURE_SEPARATION_THRESHOLD = 0.7
CREATURE_MAX_VELOCITY = 0.1
CREATURE_MIN_VELOCITY = 0.02

# Hive configuration
H_INITIAL_WORKERS = 20
H_INITIAL_QUEENS = 1
H_BEE_COOLDOWN = 3
COMB_WIDTH, COMB_HEIGHT = 12, 9
EGG_CELL_VALUE = -2

# Flower properties
F_SIZE = 8

# Background generation parameters
BG_NOISE_OCTAVES = 8
BG_NOISE_SCALE = 4
BG_WATER_THRESHOLD = 130 / 255
BG_SAND_THRESHOLD = 120 / 255
BG_COLOUR_VIBRANCY_EXP = 0.5
BG_COLOUR_DULLNESS_EXP = 1.1
BG_TILE_BORDER_DARKEN_FACTOR = 0.5
BG_TILE_BORDER_THRESHOLD_SCALE = 16

# Initialize Pygame
pygame.init()
pygame.font.init()
STATS_FONT = pygame.font.SysFont("Arial", 16)

# Helper Functions
# ---------------

def distance(pos1: pygame.Vector2, pos2: pygame.Vector2) -> float:
    """Calculate Euclidean distance between two points.
    
    Args:
        pos1: First position vector
        pos2: Second position vector
        
    Returns:
        float: Distance between the two points
    """
    return pos1.distance_to(pos2)

def is_hovered(screen_width: int, screen_height: int, screen_pos: pygame.Vector2) -> bool:
    """Check if mouse is hovering over an object at given screen position.
    
    Args:
        screen_width: Width of object's bounding box
        screen_height: Height of object's bounding box
        screen_pos: Screen position to check
        
    Returns:
        bool: True if mouse is hovering over the position
    """
    mouse = pygame.math.Vector2(pygame.mouse.get_pos())
    return (-screen_width < mouse.x - screen_pos.x < screen_width and 
            -screen_height < mouse.y - screen_pos.y < screen_height)

def gridpos2screen(x: pygame.Vector2, camera_offset: pygame.Vector2) -> pygame.Vector2:
    """Convert grid coordinates to screen coordinates.
    
    Args:
        x: Grid position
        camera_offset: Current camera offset
        
    Returns:
        pygame.Vector2: Screen coordinates
    """
    return (x * sim.scaled - camera_offset)
    
def screenpos2grid(x: float, camera_offset: pygame.Vector2) -> float:
    """Convert screen coordinates to grid coordinates.
    
    Args:
        x: Screen position
        camera_offset: Current camera offset
        
    Returns:
        float: Grid coordinates
    """
    return ((x + camera_offset) / sim.scaled)

def hivepos2screen(x: pygame.Vector2) -> pygame.Vector2:
    """Convert hive coordinates to screen coordinates.
    
    The hive view is fixed at 400x400 pixels in the bottom-right corner
    with a 10 pixel offset. Each hive position unit equals 10 screen pixels.
    
    Args:
        x: Hive position
        
    Returns:
        pygame.Vector2: Screen coordinates
    """
    return (pygame.Vector2(WINDOW_WIDTH-410, WINDOW_HEIGHT-410) + x*10)

def screenpos2hive(x: pygame.Vector2) -> pygame.Vector2:
    """Convert screen coordinates to hive coordinates.
    
    Args:
        x: Screen position
        
    Returns:
        pygame.Vector2: Hive coordinates
    """
    return ((x - pygame.Vector2(WINDOW_WIDTH-410, WINDOW_HEIGHT-410)) / 10)

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, 
              colour: tuple, position: tuple, anchor: str = "topleft") -> None:
    """Draw text on a surface with specified parameters.
    
    Args:
        surface: Surface to draw on
        text: Text to display
        font: Font to use
        colour: RGB color tuple
        position: Position to draw at
        anchor: Text anchor point ("topleft", "center", etc.)
    """
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, position)
    surface.blit(text_surface, text_rect)

def get_sigmoid(x: float) -> float:
    """Calculate sigmoid function value.
    
    Args:
        x: Input value
        
    Returns:
        float: Sigmoid of input (between 0 and 1)
    """
    return 1 / (1 + math.exp(-x))

def load_parameters_from_file(filepath: str) -> dict:
    """Load simulation parameters from a CSV file.

    Args:
        filepath: Path to the parameter CSV file.

    Returns:
        dict: A dictionary of parameters.
    """
    parameters = {}
    try:
        with open(filepath, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    param_name, param_value = row
                    # Attempt to convert to int or float if possible
                    try:
                        if '.' in param_value:
                            parameters[param_name.strip()] = float(param_value.strip())
                        else:
                            parameters[param_name.strip()] = int(param_value.strip())
                    except ValueError:
                        parameters[param_name.strip()] = param_value.strip() # Store as string if conversion fails
                else:
                    print(f"Warning: Skipping malformed row in {filepath}: {row}")
    except FileNotFoundError:
        print(f"Error: ruh oh Parameter file {filepath} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading parameter file {filepath}: {e}")
        sys.exit(1)
    return parameters

class Environment:
    """Manages the simulation environment including terrain generation and rendering.
    
    The environment consists of a procedurally generated world using Perlin noise
    to create varied terrain including water, sand and land. It handles the 
    background rendering with proper caching for performance.
    
    Attributes:
        map_world_surface (pygame.Surface): Surface for the world map
        maparr (np.ndarray): 2D array storing terrain height values
        map_col (np.ndarray): 2D array storing terrain colors
        cached_bg (pygame.Surface): Cached background surface for performance
        cached_camera_offset (pygame.Vector2): Last camera position for cache
        cached_scaled (float): Last scale factor for cache
    """
    
    def __init__(self, size: int, manager):
        """Initialize the environment.
        
        Args:
            size: Size of the world grid
            manager: Simulation manager instance
        """
        self.map_world_surface = pygame.Surface((size, size))
        self.generate_background_texture(size)
        
        # Initialize caching variables
        self.cached_bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.cached_camera_offset = pygame.Vector2(-1, -1)
        self.cached_scaled = -1

    def load_map_from_file(self, filepath: str, map_size_param: int) -> None:
        """Load map terrain data from a CSV file.

        Args:
            filepath: Path to the map CSV file.
            map_size_param: The expected size of the map (MAP_SIZE).
        """
        try:
            loaded_map_data = []
            with open(filepath, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row_index, row in enumerate(reader):
                    if len(row) != map_size_param:
                        print(f"Error: Map file {filepath} row {row_index+1} has incorrect number of columns. Expected {map_size_param}, got {len(row)}.")
                        sys.exit(1)
                    try:
                        loaded_map_data.append([float(val) for val in row])
                    except ValueError as e:
                        print(f"Error: Non-numeric value found in map file {filepath} at row {row_index+1}: {e}")
                        sys.exit(1)
            
            if len(loaded_map_data) != map_size_param:
                print(f"Error: Map file {filepath} has incorrect number of rows. Expected {map_size_param}, got {len(loaded_map_data)}.")
                sys.exit(1)

            self.maparr = np.array(loaded_map_data, dtype=float)
            
            # Validate that all values are between 0 and 1 (inclusive)
            if not np.all((self.maparr >= 0) & (self.maparr <= 1)):
                print(f"Error: Map file {filepath} contains values outside the expected range [0, 1].")
                sys.exit(1)

            self.map_col = np.empty((map_size_param, map_size_param), dtype=object)
            for i in range(map_size_param):
                for j in range(map_size_param):
                    self.map_col[i][j] = self.get_tile_colour(self.maparr[i][j])
            
            print(f"Successfully loaded map from {filepath}")

        except FileNotFoundError:
            print(f"Error: Map file {filepath} not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading map file {filepath}: {e}")
            sys.exit(1)

    def generate_background_texture(self, size: int) -> None:
        """Generate the background terrain using Perlin noise.
        
        Creates a natural-looking terrain with water, sand and land areas
        using Perlin noise for smooth transitions between different regions.
        
        Args:
            size: Size of the world grid
        """
        # Use consistent offsets based on seed
        x_offset = random.randint(0, 10000)
        y_offset = random.randint(0, 10000)
        
        self.maparr = np.zeros((size, size), dtype=float)
        self.map_col = np.empty((size, size), dtype=object)

        for i in range(size):
            for j in range(size):
                # Generate Perlin noise value
                noise_value = pnoise2(
                    (i + x_offset) * BG_NOISE_SCALE / size,
                    (j + y_offset) * BG_NOISE_SCALE / size,
                    BG_NOISE_OCTAVES
                )
                noise_value = (noise_value + 1) / 2  # Normalize to 0-1 range
                self.maparr[i][j] = noise_value
                self.map_col[i][j] = self.get_tile_colour(noise_value)

    def get_tile_colour(self, pno: float) -> tuple:
        """Convert Perlin noise value to terrain color.
        
        Args:
            pno: Perlin noise value (0-1)
            
        Returns:
            tuple: RGB color values for the terrain
        """
        # Ensure pno is within expected 0-1 range, helps prevent math errors with exponents
        pno = max(0.0, min(1.0, pno))

        c_float = 255 * (pno**BG_COLOUR_DULLNESS_EXP)
        fav_float = 255 * (pno**BG_COLOUR_VIBRANCY_EXP)

        # Base values, rounded and clamped
        c = max(0, min(255, int(round(c_float))))
        fav = max(0, min(255, int(round(fav_float))))

        if pno >= BG_WATER_THRESHOLD:
            # Water tiles - blue tones
            r = max(0, min(255, int(round(220 - c_float))))
            g = max(0, min(255, int(round(200 - (c_float / 2.0)))))
            b = fav # fav is already calculated from fav_float, rounded and clamped
            return (r, g, b)
        elif BG_SAND_THRESHOLD < pno < BG_WATER_THRESHOLD:
            # Sand tiles - yellow tones
            # fav is already calculated, rounded and clamped
            # c is already calculated, rounded and clamped
            return (fav, fav, c)
        else:
            # Land tiles - green tones
            r = c # c is already calculated, rounded and clamped
            g = max(0, min(255, int(round(fav_float + 15))))
            b = max(0, min(255, int(round(c_float - 10))))
            return (r, g, b)

    def update_background(self, size: int, camera_offset: pygame.Vector2, scaled_value: float) -> pygame.Surface:
        """Update the background surface if camera or scale changed.
        
        Args:
            size: World grid size
            camera_offset: Current camera position
            scaled_value: Current scale factor
            
        Returns:
            pygame.Surface: Updated background surface
        """
        if (camera_offset != self.cached_camera_offset or scaled_value != self.cached_scaled):
            self.actually_update_background(self.cached_bg, size, camera_offset, scaled_value)
            self.cached_camera_offset = camera_offset
            self.cached_scaled = scaled_value

        return self.cached_bg

    def actually_update_background(self, target_surface: pygame.Surface, size: int, 
                                 camera_offset: pygame.Vector2, scaled: float) -> None:
        """Render the visible portion of the background.
        
        Only renders the tiles that are currently visible in the viewport
        for better performance. Uses precise pixel calculations to prevent gaps.
        
        Args:
            target_surface: Surface to draw on
            size: World grid size
            camera_offset: Current camera position
            scaled: Current scale factor
        """
        target_surface.fill(BACKGROUND_FILL_COLOUR)

        # Calculate visible region
        start_col = max(0, math.floor(camera_offset.x / scaled))
        end_col = min(size, math.ceil((WINDOW_WIDTH + camera_offset.x) / scaled))
        start_row = max(0, math.floor(camera_offset.y / scaled))
        end_row = min(size, math.ceil((WINDOW_HEIGHT + camera_offset.y) / scaled))

        for i in range(start_col, end_col):
            for j in range(start_row, end_row):
                col = self.map_col[i][j]
                
                # Calculate floating-point screen coordinates for the tile's corners
                screen_x_start_float = i * scaled - camera_offset.x
                screen_y_start_float = j * scaled - camera_offset.y
                screen_x_end_float = (i + 1) * scaled - camera_offset.x
                screen_y_end_float = (j + 1) * scaled - camera_offset.y

                # Round coordinates to nearest pixel for drawing
                draw_x = round(screen_x_start_float)
                draw_y = round(screen_y_start_float)
                
                # Calculate width and height based on the difference of rounded edge coordinates
                draw_w = round(screen_x_end_float) - draw_x
                draw_h = round(screen_y_end_float) - draw_y
                
                # Draw the tile fill only if width and height are positive
                if draw_w > 0 and draw_h > 0:
                    pygame.draw.rect(target_surface, col, 
                                   (draw_x, draw_y, draw_w, draw_h))
                
                    # Draw the border if enabled and tile is visible
                    if scaled > BG_TILE_BORDER_THRESHOLD_SCALE:
                        border_color = tuple(int(c * BG_TILE_BORDER_DARKEN_FACTOR) for c in col)
                        pygame.draw.rect(target_surface, border_color,
                                       (draw_x, draw_y, draw_w, draw_h), 1)

# 
# CLASSES
#

class Simulation():
    def __init__(self, initial_world_size=4096):
        #prev global variables
        self.scaled = initial_world_size/MAP_SIZE
        self.frames = 0

        self.number_of_bees = H_INITIAL_WORKERS
        self.initial_bee_energy = CREATURE_INITIAL_ENERGY
        self.hive_release_cooldown = H_BEE_COOLDOWN
        self.number_obstacles = N_OBSTACLES
        self.number_of_hives = 10 # Default number of hives

        self.creatures = []
        self.hives = []
        self.flowers = []
        self.selected_bee = None
        self.selected_hive = None
        self.camera_offset = pygame.Vector2(0,0)

        self.obstacles = []

        self.obstaclemap = np.zeros((MAP_SIZE+1, MAP_SIZE+1))

        self.background = None

        # Population graph attributes
        self.population_history = []
        self.graph_update_interval = FPS # Update graph data once per second
        self.max_history_points = 200 # Store last 100 data points for the graph
        self.graph_rect = pygame.Rect(WINDOW_WIDTH - 230, 10, 220, 100) # Position and size
        self.graph_bg_color = (30, 30, 30, 180) # Semi-transparent dark background
        self.graph_line_color = (0, 255, 0) # Green line for population
        self.graph_axis_color = (150, 150, 150)
        self.graph_text_color = (200, 200, 200)

    def update_values(self, number_of_bees, initial_bee_energy, hive_release_cooldown, number_obstacles, number_of_hives):
        self.number_of_bees = number_of_bees
        self.initial_bee_energy = initial_bee_energy
        self.hive_release_cooldown = hive_release_cooldown
        self.number_obstacles = number_obstacles
        self.number_of_hives = number_of_hives
        
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
        temp_bee = Creature(hive.pos.x, hive.pos.y, hive, self, "worker")
        self.add(temp_bee)
        hive.bees_inside.append(temp_bee)
        temp_bee.hive_pos = pygame.Vector2(spawn_pos)

    def add_obstacles(self, obstacle):
        self.obstacles.append(obstacle)
        centre_x = int(obstacle.pos.x)
        centre_y = int(obstacle.pos.y)
        size=obstacle.size
        for i in range(2*obstacle.size):
            pos_x = centre_x - obstacle.size + i
            for j in range(2*obstacle.size):
                pos_y = centre_y - obstacle.size + j
                if (i == 0 or i == 2*obstacle.size-1) or (j == 0 or j == 2*obstacle.size-1):
                    self.obstaclemap[pos_x, pos_y] = 1

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

        # Update population history for the graph
        if self.frames % self.graph_update_interval == 0:
            current_population = len(self.creatures)
            self.population_history.append(current_population)
            if len(self.population_history) > self.max_history_points:
                self.population_history = self.population_history[-self.max_history_points:] # Keep last N points

        self.show_selected()
        self.check_mouse_movement()
        self.draw_population_graph() # Draw the population graph

    def check_mouse_movement(self):
        mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        mouse_offset = pygame.Vector2(0,0)

        if mouse.y <= 0:
            mouse_offset.y = -25
        elif mouse.y >= WINDOW_HEIGHT - 1:
            mouse_offset.y = 25
        
        if mouse.x == 0:
            mouse_offset.x = -25
        elif mouse.x >= WINDOW_WIDTH - 1:
            mouse_offset.x = 25

        self.camera_offset = self.camera_offset + mouse_offset
        self.camera_offset.x = max(0, min(self.camera_offset.x, self.scaled * MAP_SIZE - WINDOW_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.scaled * MAP_SIZE - WINDOW_HEIGHT))

    def handle_click(self, click_pos_screen, camera_offset):
        clicked = False
        click_vec = pygame.Vector2(click_pos_screen)

        self.selected_bee = None
        self.selected_hive = None
        
        if not clicked:
            for hive in reversed(self.hives):
                screen_pos = gridpos2screen(hive.pos, camera_offset)
                diff = pygame.math.Vector2.magnitude(screen_pos-click_vec)
                if diff <= hive.size/2:
                    self.selected_hive = hive
                    clicked = True

        if not clicked:
            for bee in reversed(self.creatures):
                screen_pos = gridpos2screen(bee.pos, camera_offset)
                diff = pygame.math.Vector2.magnitude(screen_pos - click_vec)
                if diff <= bee.radius:
                    self.selected_bee = bee
                    clicked = True

    def add_objs(self, maparr):
        invalid_coords = []

        for i in range(self.number_of_hives): # Use configured number of hives
            random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            while maparr[int(random_coord.x)][int(random_coord.y)] >= BG_WATER_THRESHOLD or random_coord in invalid_coords:
                random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            sim.add_hive(Hive(random_coord.x,random_coord.y, sim, self))
            invalid_coords.append(random_coord)

        for i in range(25):
            random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            while maparr[int(random_coord.x)][int(random_coord.y)] >= BG_WATER_THRESHOLD or random_coord in invalid_coords:
                random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            sim.add_flo(Flower(random_coord.x, random_coord.y))
            invalid_coords.append(random_coord)

        for i in range(self.number_obstacles):
            random_coord = pygame.Vector2(random.randint(5,123),random.randint(5,123))
            while maparr[int(random_coord.x)][int(random_coord.y)] >= BG_WATER_THRESHOLD or random_coord in invalid_coords:
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
            for comb_centre in self.selected_hive.combs:
                honey = self.selected_hive.combs_honey[math.floor(i/COMB_WIDTH), i % COMB_WIDTH]
                if honey > 0: # does not draw invalid combs (-1)
                    col.hsla =((20+40*honey/100, 100, 50*honey/100+15, 100))
                    h_pos = hivepos2screen(pygame.Vector2(comb_centre))
                    pygame.draw.circle(screen, (col.r, col.g, col.b), h_pos, 10)
                if honey <=-2:
                    col.hsla = (0, 100, max(min(50 * (-honey-1)/30 + 15,100),0), 100)
                    h_pos = hivepos2screen(pygame.Vector2(comb_centre))
                    pygame.draw.circle(screen, (col.r, col.g, col.b), h_pos, 10)
                i+=1

            for bee in self.selected_hive.bees_inside:
                bee.draw_inside_hive()

    def draw_population_graph(self):
        # Draw background for the graph
        graph_surface = pygame.Surface(self.graph_rect.size, pygame.SRCALPHA)
        graph_surface.fill(self.graph_bg_color)
        screen.blit(graph_surface, self.graph_rect.topleft)

        # Draw border for the graph area
        pygame.draw.rect(screen, self.graph_axis_color, self.graph_rect, 1)
        
        # Draw Title
        draw_text(screen, "Bee Population", STATS_FONT, self.graph_text_color, 
                  (self.graph_rect.centerx, self.graph_rect.top + 5), anchor="midtop")

        if len(self.population_history) < 2:
            # Not enough data to draw a line
            info_text = "Collecting data..." if not self.population_history else f"Pop: {self.population_history[0]}"
            draw_text(screen, info_text, STATS_FONT, self.graph_text_color,
                      self.graph_rect.center, anchor="center")
            return

        max_pop = max(self.population_history) if self.population_history else 1
        min_pop = min(self.population_history) if self.population_history else 0
        
        # Adjust max_pop slightly for padding if all values are the same or min_pop == max_pop
        if max_pop == min_pop:
            max_pop += 1 # Avoid division by zero and give some space

        points = []
        history_len = len(self.population_history)
        
        padding_y = 15 # Pixels from top and bottom of graph area for text
        drawable_height = self.graph_rect.height - 2 * padding_y
        
        for i, pop_count in enumerate(self.population_history):
            # X coordinate: evenly spaced across the graph width
            x = self.graph_rect.left + (i / (self.max_history_points -1)) * self.graph_rect.width \
                if self.max_history_points > 1 else self.graph_rect.left # Handle case of 1 point
            
            # Y coordinate: scaled population count
            # Ensure pop_count is within [min_pop, max_pop] for scaling
            # Scale pop_count to fit within drawable_height
            # Invert Y because Pygame's Y is 0 at top
            y_scaled_value = 0
            if (max_pop - min_pop) > 0: # Avoid division by zero
                 y_scaled_value = (pop_count - min_pop) / (max_pop - min_pop)

            y = self.graph_rect.bottom - padding_y - (y_scaled_value * drawable_height)
            
            points.append((x, y))

        if len(points) >= 2:
            pygame.draw.lines(screen, self.graph_line_color, False, points, 1)

        # Draw current and max population text
        current_pop_text = f"Now: {self.population_history[-1]}"
        max_pop_text = f"Max: {max(self.population_history)}" # Recalculate for display based on current history
        
        draw_text(screen, current_pop_text, STATS_FONT, self.graph_text_color,
                  (self.graph_rect.left + 5, self.graph_rect.bottom - padding_y + 2), anchor="bottomleft")
        draw_text(screen, max_pop_text, STATS_FONT, self.graph_text_color,
                  (self.graph_rect.right - 5, self.graph_rect.bottom - padding_y + 2), anchor="bottomright")

class Flower:
    """Represents a flower in the simulation that bees can collect pollen from.
    
    Flowers are static objects that provide resources (pollen) for bees to collect.
    They have a visual representation and track how many bees are currently
    visiting them.
    
    Attributes:
        pos (pygame.Vector2): Position in the world grid
        size (int): Size of the flower
        petal_color (tuple): RGB color of the flower petals
        pollen (float): Amount of pollen available
        n_bees (int): Number of bees currently visiting
        angle (float): Current rotation angle
        rot_speed (float): Speed of rotation animation
    """
    
    def __init__(self, x: float, y: float):
        """Initialize a flower.
        
        Args:
            x: X-coordinate in the world grid
            y: Y-coordinate in the world grid
        """
        self.pos = pygame.Vector2(x, y)
        self.size = F_SIZE
        self.petal_color = (
            random.randint(100, 255),
            255,
            random.randint(100, 255)
        )
        self.pollen = 100000
        self.n_bees = 0
        self.angle = 0
        self.rot_speed = 0.005
    
    def update(self, manager) -> None:
        """Update flower state and render.
        
        Handles pollen depletion and removes the flower if depleted.
        
        Args:
            manager: Simulation manager instance
        """
        self.draw(manager.camera_offset, manager.scaled)
        
        if self.pollen <= 0:
            manager.rem_flo(self)

    def draw(self, camera_offset: pygame.Vector2, scaled: float) -> None:
        """Draw the flower on the screen.
        
        Args:
            camera_offset: Current camera position
            scaled: Current scale factor
        """
        screen_pos = gridpos2screen(self.pos, camera_offset)
        pygame.draw.circle(screen, self.petal_color, screen_pos, scaled)
        draw_text(screen, f"{self.n_bees}", STATS_FONT, TEXT_COLOUR, screen_pos)

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
        """Initialize a hive.
        
        Args:
            x: X-coordinate in the world grid
            y: Y-coordinate in the world grid
            sim: Simulation instance
            manager: Simulation manager instance
        """
        self.pos=pygame.Vector2(x,y)
        self.workerspop = manager.number_of_bees
        self.dronespop = self.workerspop
        self.queenpop = H_INITIAL_QUEENS
        self.bees_inside = []
        self.bees_outside = []
        
        self.internal_cooldown = 0

        self.beelook = 0

        self.size = self.workerspop + self.queenpop

        for i in range(self.workerspop):
            offset_pos = [((random.random()-0.5)*100), ((random.random()-0.5)*100)]
            temp_bee = Creature(x,y, self, manager, "worker")
            sim.add(temp_bee)
            self.bees_inside.append(temp_bee)

        for i in range(self.queenpop):
            offset_pos = [((random.random()-0.5)*100), ((random.random()-0.5)*100)]
            temp_bee = Creature(x,y, self, manager, "queen")
            sim.add(temp_bee)
            self.bees_inside.append(temp_bee)

        self.combs = []
        self.combs_honey = np.zeros((9,12))
        radius = 1
        radius_long = radius/np.cos(np.pi/6)
        tringle_len = radius*np.tan(np.pi/6)

        horizontal_diff = 2*radius
        for i in range(9):
            y_pos = (5 + i*(2*radius_long))
            if i % 2 == 0:
                offset_val = radius
            else:
                offset_val = 0
            for j in range(12):
                x_pos = 5 + j * (horizontal_diff) + offset_val
                self.combs.append((x_pos, y_pos))

                fake_comb_value = -1

                self.combs_honey[i, j] = 0
                if ((j == 0) and (i - 3 <= 0)) or ((j==1) and (i-1 <= 0)):
                    self.combs_honey[i,j] = fake_comb_value
                if ((j==0) and (i+4) >= COMB_HEIGHT) or ((j==1) and (i+2 >= COMB_HEIGHT)):
                    self.combs_honey[i,j] = fake_comb_value
                if ((j == COMB_WIDTH-1) and (i-2 <= 0)) or ((j==COMB_WIDTH-2) and (i <= 0)):
                    self.combs_honey[i,j] = fake_comb_value
                if ((j== COMB_WIDTH-1) and (i+3) >= COMB_HEIGHT) or ((j== COMB_WIDTH-2) and (i+1 >= COMB_HEIGHT)):
                    self.combs_honey[i,j] = fake_comb_value

    def update(self, manager):
        if self.beelook >= len(self.bees_inside):
            self.beelook = 0

        if manager.frames % 60 == 1:
            self.update_eggs(manager)

        self.size = manager.scaled*4
        if self.internal_cooldown == 0 and len(self.bees_inside) > 0:
            bee = self.bees_inside[self.beelook]
            if bee.seeking_honey == True:
                self.bees_inside.pop(self.beelook)
                self.bees_outside.append(bee)
            else:
                self.beelook += 1
            self.internal_cooldown = manager.hive_release_cooldown
        elif self.internal_cooldown > 0 :
            self.internal_cooldown -= 1

        self.draw(manager.camera_offset)

    def update_eggs(self, manager):
        """this updates the hive every time its called, which is like every 60 frames i think"""
        for r_egg, row_data in enumerate(self.combs_honey):
            for c_egg, egg_value_at_iteration_start in enumerate(row_data):
                if egg_value_at_iteration_start <= EGG_CELL_VALUE:  # Is it an egg cell?
                    # Decrement the egg value in the hive's storage
                    self.combs_honey[r_egg, c_egg] -= 1
                    
                    # Check for maturation using the egg's value *before* this frame's decrement
                    if egg_value_at_iteration_start <= -30:  # Egg fully matured (threshold is -30)
                        # Search for cells with > 80 honey
                        honey_rows, honey_cols = np.where(self.combs_honey > 80) # Honey requirement is 80
                        
                        if honey_rows.size >= 2: # Check if there are at least 5 cells with enough honey
                            # Consume honey from the first 5 found cells
                            for i in range(2):
                                r_honey_consume, c_honey_consume = honey_rows[i], honey_cols[i]
                                self.combs_honey[r_honey_consume, c_honey_consume] = 0
                            
                            # Reset egg cell (which was just decremented, now set to -1)
                            self.combs_honey[r_egg, c_egg] = -1 

                            # Spawn bee
                            flat_egg_cell_idx = r_egg * COMB_WIDTH + c_egg
                            manager.spawn_new_bee(self, self.combs[flat_egg_cell_idx])
                            
                            return # Spawn one bee per update_eggs call and exit

    def draw(self, camera_offset):
        """draws the hive onto the screen"""
        screen_pos = gridpos2screen(self.pos, camera_offset)
        pygame.draw.rect(screen, (255, 255, 0), (screen_pos.x-self.size/2, screen_pos.y-self.size/2, self.size, self.size))
        draw_text(screen, f"{len(self.bees_inside) + len(self.bees_outside)}", STATS_FONT, (0,0,0), screen_pos)

class Creature():
    def __init__(self, x, y, hive, manager, role):
        """initialises the properties of the creature :DDD"""
        self.role = role

        self.pos = pygame.Vector2(x, y) #change pos later 
        
        self.energy = random.randint(round(manager.initial_bee_energy/2), round(manager.initial_bee_energy)) 

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

        self.eggs = 100 # all start off with 0 eggs, only queen bees are able to "produce" eggs

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

        self.image_file = pygame.image.load('bee.png') # this is not used but it doesnt affect the rest of the code so its still here. why not

        # im not entirely sure if this actually does anything

    def update(self, manager):
        self.avoidedge() # clamps position to borders, does not avoid (diff function)
        # for some reason i decided to change the avoidedge to a new function but i cbb changing every instance
        # this is called after i changed this to position clamp. (so saurry)

        """This (below) is unsed a_star_pathfind code. It doesnt effect physics or the simulation at all and purely visual. 
        It looks nice (and interesting!), but I have found little reason to use it on top of the bee's already complex behaviour. 
        This pathfinding *could* circumvent a very rare issue (that is the bee getting stuck between two rocks), 
        but since the map is too big and there is too little obstacles, i have decided not to use it.

        Moreover, it isnt really true to real life animal behaviour - animals rarely calculate the most "optimal" direction when heading towards an object, 
        as animals are incapable of storing the position of their target object and every obstacle in their path."""
        # uncomment below for a* pathfind to a random location visualised
        # if manager.frames == 1:
        #     # get a non water pos
        #     random_pos = pygame.Vector2(random.randint(0,127), random.randint(0,127))
        #     while manager.background.maparr[int(random_pos.x), int(random_pos.y)] >= BG_WATER_THRESHOLD:
        #         random_pos = pygame.Vector2(random.randint(0,127), random.randint(0,127))
        #
        #     self.a_star_pathfind(manager, self.hive.pos, random_pos)

        is_worker = self.role == "worker" # boolean true if worker 
        is_outside = self in self.hive.bees_outside # boolean true if outside

        steering = pygame.Vector2(0,0)

        if self.role == "queen":
            if manager.frames % 60 == 0:
                self.eggs += 1


        if is_worker: # if bee is worker
            self.whatamidoing() # checks if needs to search for honey 

        if is_outside: # if bee is outside
            # calculate forces every 5 frames. this saves computational oad
            if manager.frames % 5 == self.selectedframe: # selected frame makes sure that bees calculate forces at different frames
                steering += self.calculateForces(self.hive.bees_outside, self.pos, manager) # calculates all the forces to do/adds

            steering += self.calculate_avoid_edge_force(self.pos, 0, MAP_SIZE, 1) * 100
            steering += self.avoidrock(self.pos, manager)
            
            if is_worker:
                self.seekFlowers(manager.flowers)

            steering += self.avoidwater(manager.background.maparr) * 0.8
        elif not is_outside: # inside considered
            steering += self.calculate_avoid_edge_force(self.hive_pos, 0, 40, 1) * 100

            if self in self.hive.bees_inside:
                steering += self.calculateForces(self.hive.bees_inside, (self.hive_pos), None)

                if self.seeking_honey == False or self.role == 'queen':
                    steering += self.dohoneythings() * 2.5 # function to fill up the honey

        if self.role == "drone":
            print("hullo i am a drone", is_outside, self.pos)


        self.applyForce(steering)
        self.velocity += self.acceleration
        self.acceleration *= 0 # reset acceleration

        
        fac = 30 # angle factor
        rotate = (random.random() - 0.5)*fac # random steering force

        self.velocity = pygame.math.Vector2.rotate(self.velocity, rotate)
        
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        if self.speed >= CREATURE_MAX_VELOCITY:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * CREATURE_MAX_VELOCITY
        if 0 < self.speed <= CREATURE_MIN_VELOCITY:
            self.velocity = pygame.math.Vector2.normalize(self.velocity) * CREATURE_MIN_VELOCITY
        self.speed = pygame.math.Vector2.magnitude(self.velocity)

        if is_outside:
            self.pos += self.velocity
        else:
            self.hive_pos += self.velocity
        
        self.selected = (manager.selected_bee == self)

        if manager.frames % FPS == 0 and self.role != "queen":  # queens dont die!
            self.energy = self.energy - CREATURE_ENERGY_DECAY_RATE
            # print(self.energy)

        if self.energy <= 0:
            # print("creature ran out of energy :(")
            self.closestflower.n_bees -= 1
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
        """Checks to see if the bee has enough honey"""
        self.min_honey = 80 # Min Honey

        if self.honey >= self.min_honey: # If more than min
            self.seeking_honey = False # No longer seeking!

    def a_star_pathfind(self, manager, in_pos, target_pos):
        """note about this implementation:
        1. only works on grid (in this case MAP_SIZExMAP_SIZE which is 128x)
        2. i am schizophrenic so this might not wor
        3. this is based off random pseudocode i found in google images
        i actually spent some time debugging this. but i just didnt find it productive to run this
        expensive computation. realistically bees do not know the perfect path to any object so this is
        left as is
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
            # gets 3x3 grid around centre

            children = []
            for i in range(-1,2): #i is x 
                for j in range(-1,2): # j is you
                    if (i == 0 and j == 0): # if centred
                        continue

                    node_pos = pygame.Vector2(current_node.position.x + i, current_node.position.y + j)
                    
                    if not (0 <= node_pos.x < MAP_SIZE and 0 <= node_pos.y < MAP_SIZE):
                        continue

                    if manager.background.maparr[int(node_pos.x), int(node_pos.y)] >= BG_WATER_THRESHOLD:
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
            if distance(self.pos, self.closestflower.pos) <= CREATURE_DETECTION_RADIUS/4:
                self.honey += 0.5
                self.total_honey += 0.5
                # self.closestflower.pollen -= 0.5 pollen does not introduce the behavi
                self.energy = min(self.energy + 0.5, CREATURE_INITIAL_ENERGY) # Replenish energy
        elif self.seeking_honey == False: # If it is no longer seeking honey.
            self.goHive()
    
    def goFlower(self):
        # get vector from closest flower and itself
        # im not sure why but the current implementation the bees are circling the flowers
        if distance(self.pos, self.closestflower.pos) <= CREATURE_DETECTION_RADIUS*3: 
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
        # known error   File "/Users/thomas/Desktop/Code/School/Assignments/Assessment/main.py", line 686, in enter_hive
        # self.hive.bees_outside.remove(self)
        # ValueError: list.remove(x): x not in list

    def calculateForces(self, bees, beepos, manager):
        """This Function Calculates the basic movement of the bees following the rules of boids"""
        # behaviours of bees: 
        # 1. flocking: boid behaviour with their 3 rules: 1. avoid other bees, 2. same speed as other bees, tend towards the centre of a flock
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

                if (0 < diff_mag < CREATURE_SEPARATION_THRESHOLD):
                    force += pygame.math.Vector2.normalize(diff) * (CREATURE_SEPARATION_THRESHOLD-diff_mag)/(CREATURE_SEPARATION_THRESHOLD)


        return force

    def avoidwater(self, maparr):
        force = pygame.Vector2(0,0)

        # print(maparr)
        if self.speed == 0 or maparr.all == None:
            return force
        
        direction = pygame.math.Vector2.normalize(self.velocity)
        look_pos = pygame.Vector2(0)
        look_pos.x = max(0, min(self.pos.x + direction.x, MAP_SIZE - 1))
        look_pos.y = max(0, min(self.pos.y + direction.y, MAP_SIZE - 1))
        # print(self.pos, look_pos)

        if (maparr[int(look_pos.x)][int(look_pos.y)]) >= BG_WATER_THRESHOLD:
            force -= direction

        return force

    
    def calculate_avoid_edge_force(self, beepos, min_bound, max_bound, strength_multiplier):
        force = pygame.Vector2(0,0)
        
        margin = AVOID_EDGE_MARGIN 
        base_strength = AVOID_EDGE_STRENGTH * strength_multiplier # Allow dynamic strength

        if beepos.x <= min_bound+margin:
            force.x += base_strength * (margin - (beepos.x-min_bound))
        elif beepos.x >= max_bound-margin:
            force.x -= base_strength * (margin - (max_bound - beepos.x))


        if beepos.y <= min_bound+margin:
            force.y+=base_strength * (margin - (beepos.y-min_bound))

        elif beepos.y >= max_bound - margin:
            force.y-=base_strength * (margin - (max_bound - beepos.y))

        return force

    def avoidedge(self):
        """Despite saying avoid, in reality it clamps the bees position
        The real avoid function occurs later."""
        if self in self.hive.bees_outside: # Checks if it is outside
            self.pos.x = max(0, min(self.pos.x, MAP_SIZE - 0.01)) # Clamps from 0-MAP_SIZE range for array indexing
            self.pos.y = max(0, min(self.pos.y, MAP_SIZE - 0.01)) # Same thing here
        else: # Else, (basically if inside)
            self.hive_pos.x = max(0, min(self.hive_pos.x, 39.99)) # Clamps 0-40
            self.hive_pos.y = max(0, min(self.hive_pos.y, 39.99)) # same thing

        # note to self: add bottom left right border  too! future note: done!

    def separation(self, bees, beepos):
        sepForce = pygame.Vector2(0,0)

        for bee in bees: 
            if beepos == self.hive_pos:
                detectpos = bee.hive_pos
            else: detectpos = beepos

            dist = distance(detectpos, beepos)

            if dist <= CREATURE_DETECTION_RADIUS and detectpos != beepos:
                diffVec = detectpos - beepos
                if abs(dist) <= CREATURE_SEPARATION_THRESHOLD:
                    nomVec = pygame.Vector2.normalize(diffVec)
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
            if 0 < dist <= CREATURE_DETECTION_RADIUS and detectpos != beepos:
                avgV += bee.velocity
                counter += 1

        if counter != 0 and pygame.Vector2.magnitude(avgV) != 0:
            alignV = avgV/counter
            alignD = pygame.Vector2.normalize(alignV) * self.speed * 0.5
            return(alignD)
        
        return (avgV)

    # aims the bee towards to centre of the ""flock""
    def cohesion(self, bees, beepos):
        com = pygame.Vector2(0,0) # centre of mass
        counter = 0
        for bee in bees:
            if beepos == self.hive_pos:
                detectpos = bee.hive_pos
            else: detectpos = bee.pos

            dist = distance(detectpos, beepos)
            if 0 < dist <= CREATURE_DETECTION_RADIUS and detectpos != beepos:
                counter += 1
                com += detectpos

        if counter != 0 and com != beepos:
            com /= counter
            diff = com - beepos

            if pygame.math.Vector2.magnitude(diff) == 0:
                return (com)

            dir = pygame.Vector2.normalize(diff) * self.speed
            return(dir)
        return (com)
        
    def draw(self, scaled):
        pygame.draw.circle(screen, self.colour, self.screen_pos, (self.size_scaled+3)) 
        if self.selected == True:
            pygame.draw.circle(screen, CREATURE_HOVER_COLOUR, self.screen_pos, (self.size_scaled+4), 2) 
            pygame.draw.circle(screen, CREATURE_HOVER_COLOUR, self.screen_pos, self.size_scaled+CREATURE_DETECTION_RADIUS*scaled, 2)
            pygame.draw.circle(screen, (255,0,0), self.screen_pos, self.size_scaled+CREATURE_SEPARATION_THRESHOLD*scaled, 2)

    def dohoneythings(self):
        i = 0
        j = 0

        diff = pygame.Vector2(0,0)
        nomForce = pygame.Vector2(0,0)

        # check honey status
        if self.honey <= 0 and self.role == 'worker':
            # print("im removing myself (from hive)")
            self.seeking_honey = True
            self.hive.bees_outside.append(self)
            self.hive.bees_inside.remove(self)

        comb_pos = None
        for comb_honey in self.hive.combs_honey:
            for comb_honey_actual in comb_honey:
                comb_pos = pygame.math.Vector2(self.hive.combs[i][0], self.hive.combs[i][1])
                lowest_egg = -1
                if self.role == 'worker':
                    if 0 <= comb_honey_actual <= 100:
                        diff = comb_pos - self.hive_pos
                        if pygame.math.Vector2.magnitude(diff) <= 1 and self.honey >= 0:
                            self.honey = max(self.honey - 0.1, 0)
                            self.hive.combs_honey[j, i%COMB_WIDTH] += 0.1
                            self.energy = min(self.energy + 0.5, CREATURE_INITIAL_ENERGY) # Replenish energy
                elif self.role == 'queen':
                    if lowest_egg <= comb_honey_actual <= -1:
                        lowest_egg = comb_honey_actual
                        diff = comb_pos - self.hive_pos
                        if pygame.math.Vector2.magnitude(diff) <= 1 and self.eggs > 0:
                            self.eggs -= 1
                            self.hive.combs_honey[j, i%COMB_WIDTH] -= 1
                i+=1
            j+=1

        if comb_pos:
            if pygame.math.Vector2.magnitude(diff) != 0:
                nomForce = pygame.math.Vector2.normalize(diff) * self.speed
        return (nomForce)
            
    def draw_inside_hive(self):
        size = self.energy/20

        if self.role == "queen":
            size *= 5
            pygame.draw.circle(screen, (255, 0, 0), hivepos2screen(self.hive_pos), size+2, 2) 
        pygame.draw.circle(screen, self.colour, hivepos2screen(self.hive_pos), size)



parser = argparse.ArgumentParser(description="Simulate Bees")

parser.add_argument('-i', '--interactive', action='store_true', help='interactive mode')
parser.add_argument('-s', '--seed', type=int, help='random seed for terrain and spawning')
parser.add_argument('-b', '--batch', action='store_true', help='Run in batch mode. Requires -f and -p.')
parser.add_argument('-f', '--mapfile', type=str, help='Path to the map data file (e.g., map1.csv) for batch mode.')
parser.add_argument('-p', '--paramfile', type=str, help='Path to the parameter file (e.g., para1.csv) for batch mode.')

args = parser.parse_args()

# Set random seed
seed = None
param_file_path = None # Define to ensure it's available in all branches

if args.batch:
    if not args.mapfile or not args.paramfile:
        print("Error: Batch mode requires both --mapfile (-f) and --paramfile (-p) to be specified.")
        sys.exit(1)
    print("Running in batch mode.")
    param_file_path = args.paramfile
    loaded_params = load_parameters_from_file(param_file_path)

    # Update global constants and simulation parameters from the loaded file
    # This requires careful handling as many constants are currently global.
    # For now, we will update sim instance directly and relevant globals where easy.
    H_INITIAL_WORKERS = loaded_params.get('H_INITIAL_WORKERS', H_INITIAL_WORKERS)
    CREATURE_INITIAL_ENERGY = loaded_params.get('CREATURE_INITIAL_ENERGY', CREATURE_INITIAL_ENERGY)
    H_BEE_COOLDOWN = loaded_params.get('H_BEE_COOLDOWN', H_BEE_COOLDOWN)
    N_OBSTACLES = loaded_params.get('N_OBSTACLES', N_OBSTACLES)
    MAP_SIZE = loaded_params.get('MAP_SIZE', MAP_SIZE) # Ensure MAP_SIZE is updated before Environment creation
    FPS = loaded_params.get('FPS', FPS)
    # Add other parameters as needed, e.g., for Environment or Creature
    BG_NOISE_OCTAVES = loaded_params.get('BG_NOISE_OCTAVES', BG_NOISE_OCTAVES)
    BG_NOISE_SCALE = loaded_params.get('BG_NOISE_SCALE', BG_NOISE_SCALE)
    BG_WATER_THRESHOLD = loaded_params.get('BG_WATER_THRESHOLD', BG_WATER_THRESHOLD)
    BG_SAND_THRESHOLD = loaded_params.get('BG_SAND_THRESHOLD', BG_SAND_THRESHOLD)

    sim = Simulation()
    sim.update_values(H_INITIAL_WORKERS, CREATURE_INITIAL_ENERGY, H_BEE_COOLDOWN, N_OBSTACLES, 10)

    # Seed precedence: 1. param file, 2. command line, 3. time-based
    if 'SEED' in loaded_params:
        seed = int(loaded_params['SEED'])
    elif args.seed is not None:
        seed = args.seed
    else:
        seed = int(time.time())

elif args.interactive:
    try:
        print("::::::::::::::::::::::INPUTS::[Interactive Mode]::::::::::::::::::::::")
        print("Warning: Using extreme values may yield unexpected, untested and unaccounted for results. Performance could also be decreased.")
        number_of_bees = int(x) if (x := input(f"Number of bees per hive (default={H_INITIAL_WORKERS}) (1-100): ")) else H_INITIAL_WORKERS
        number_of_bees = max(1, min(number_of_bees, 100))
        
        initial_bee_energy = int(x) if (x := input(f"Bee Initial Energy (default={CREATURE_INITIAL_ENERGY}) (10-1000) WARNING: BEE SIZE SCALES WITH ENERGY!: ")) else CREATURE_INITIAL_ENERGY
        initial_bee_energy = max(10, min(initial_bee_energy, 1000))
        
        hive_release_cooldown = int(x) if (x := input(f"Hive Bee Release Cooldown (default={H_BEE_COOLDOWN}) (0-300)")) else H_BEE_COOLDOWN
        hive_release_cooldown = max(0, min(hive_release_cooldown, 300))
        
        number_obstacles = int(x) if (x := input(f"Number of obstacles (default={N_OBSTACLES}) (0-100): ")) else N_OBSTACLES
        number_obstacles = max(0, min(number_obstacles, 100))
        
        # New inputs
        N_HIVES_INTERACTIVE = 10 # Default for sim instance if not changed by input
        N_HIVES_INTERACTIVE = int(x) if (x := input(f"Number of hives (default={N_HIVES_INTERACTIVE}) (1-50): ")) else N_HIVES_INTERACTIVE
        N_HIVES_INTERACTIVE = max(1, min(N_HIVES_INTERACTIVE, 50))
        
        H_INITIAL_QUEENS = int(x) if (x := input(f"Initial queens per hive (default={H_INITIAL_QUEENS}) (0-10): ")) else H_INITIAL_QUEENS
        H_INITIAL_QUEENS = max(0, min(H_INITIAL_QUEENS, 10))
        
        CREATURE_MAX_VELOCITY = float(x) if (x := input(f"Creature Max Velocity (default={CREATURE_MAX_VELOCITY}) (0.01-1.0): ")) else CREATURE_MAX_VELOCITY
        CREATURE_MAX_VELOCITY = max(0.01, min(CREATURE_MAX_VELOCITY, 1.0))
        
        CREATURE_MIN_VELOCITY = float(x) if (x := input(f"Creature Min Velocity (default={CREATURE_MIN_VELOCITY}) (0.001-0.5): ")) else CREATURE_MIN_VELOCITY
        CREATURE_MIN_VELOCITY = max(0.001, min(CREATURE_MIN_VELOCITY, 0.5))
        CREATURE_MIN_VELOCITY = min(CREATURE_MIN_VELOCITY, CREATURE_MAX_VELOCITY) # Ensure min_vel <= max_vel
        
        CREATURE_DETECTION_RADIUS = float(x) if (x := input(f"Creature Detection Radius (default={CREATURE_DETECTION_RADIUS}) (0.1-20.0): ")) else CREATURE_DETECTION_RADIUS
        CREATURE_DETECTION_RADIUS = max(0.1, min(CREATURE_DETECTION_RADIUS, 20.0))
        
        CREATURE_SEPARATION_THRESHOLD = float(x) if (x := input(f"Creature Separation Threshold (default={CREATURE_SEPARATION_THRESHOLD}) (0.1-10.0): ")) else CREATURE_SEPARATION_THRESHOLD
        CREATURE_SEPARATION_THRESHOLD = max(0.1, min(CREATURE_SEPARATION_THRESHOLD, 10.0))
        CREATURE_SEPARATION_THRESHOLD = min(CREATURE_SEPARATION_THRESHOLD, CREATURE_DETECTION_RADIUS) # Ensure sep_thresh <= detect_radius
        
        F_SIZE = int(x) if (x := input(f"Flower Size (default={F_SIZE}): ")) else F_SIZE
        F_SIZE = max(1, min(F_SIZE, 20))
        
        sim = Simulation() # Create sim instance here for interactive mode too
        sim.update_values(number_of_bees, initial_bee_energy, hive_release_cooldown, number_obstacles, N_HIVES_INTERACTIVE)
        print("::::::::::::::::::::::[End Interactive Mode]::::::::::::::::::::::")
        if args.seed is not None:
            seed = args.seed
    except ValueError:
        print("Input Error: Check your inputs and try again. Using default values.")
        sim = Simulation() # Fallback to default sim if input error
        # Ensure global constants are at their defaults if interactive input fails before they are set
        H_INITIAL_QUEENS = 1
        CREATURE_MAX_VELOCITY = 0.1
        CREATURE_MIN_VELOCITY = 0.02
        CREATURE_DETECTION_RADIUS = 2.5
        CREATURE_SEPARATION_THRESHOLD = 0.7
        F_SIZE = 8
        if args.seed is not None:
            seed = args.seed
        else:
            seed = int(time.time())
else:
    # Default mode (no batch, no interactive)
    sim = Simulation()
    if args.seed is not None:
        seed = args.seed
    else:
        seed = int(time.time())

random.seed(seed)
print(f"Using seed: {seed}")
if param_file_path:
    print(f"Parameters loaded from: {param_file_path}")

# Initialize Pygame screen and clock AFTER potential FPS change from params
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.event.set_grab(True)

mouse = pygame.Vector2(0,0)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill(BACKGROUND_FILL_COLOUR)
screen.fill("white")

background = Environment(MAP_SIZE, sim)
sim.add_background(background)

if args.batch and args.mapfile:
    background.load_map_from_file(args.mapfile, MAP_SIZE)
else:
    # Procedural generation if not batch mode or mapfile not specified (though batch implies it)
    background.generate_background_texture(MAP_SIZE)

sim.add_objs(background.maparr)

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS: # Zoom in
                    # Increase scale, effectively zooming in. Max world size 16384.
                    new_conceptual_world_size = min(sim.scaled*MAP_SIZE * 1.5, 16384)
                    sim.scaled = new_conceptual_world_size/MAP_SIZE
                    background.cached_scaled = -1
                if event.key == pygame.K_MINUS: # Zoom out
                    # Decrease scale. Min world size 512.
                    new_conceptual_world_size = max(512, sim.scaled*MAP_SIZE / 1.5)
                    sim.scaled = new_conceptual_world_size/MAP_SIZE
                    background.cached_scaled = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    sim.handle_click(event.pos, sim.camera_offset)
        
        screen.fill(BACKGROUND_FILL_COLOUR)
        
        current_background_view = background.update_background(MAP_SIZE, sim.camera_offset, sim.scaled)

        screen.blit(current_background_view, (0,0))
        # background_surface.fill(BACKGROUND_FILL_COLOUR)
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
