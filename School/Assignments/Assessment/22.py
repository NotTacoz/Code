# Imports
import pygame # pygame is the primary library used for the simulation engine
import numpy as np # this is for np's useful array features and maths
import random # ensure randomised simulation on every run
import math # additional math functions
import sys # for logging, debugging
from noise import pnoise2 # map generation
from typing import List, Tuple, Optional, Dict, Any

# Constants
# Window & Display
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FPS = 60
BACKGROUND_FILL = (50, 50, 50)
TEXT_COLOUR = (255, 255, 255)

# World & Map
INITIAL_WORLD_SIZE = 4096 # Initial size of the world grid
MAP_SIZE = 128            # Number of tiles in one dimension of the map
OBJECT_SPAWN_MARGIN = 5   # Margin from map edges for spawning objects
N_OBSTACLES = 30          # Number of obstacles to generate

# Camera
CAMERA_SCROLL_SPEED = 25  # Pixels per frame for camera movement at edge
CAMERA_BORDER_MARGIN = 5  # (Currently unused) Margin for camera movement trigger

# Creature (Bee)
CR_INITIAL_ENERGY = 100     # Initial energy of a new creature
CR_ENERGY_DECAY = 1         # Energy lost per second
CR_HOVER_COLOUR = (0, 255, 0) # Colour for highlighting selected creature
BEE_DETECTION_RADIUS = 2.5  # Radius for detecting other bees/flowers
BEE_SEPARATION_THRESHOLD = 0.7 # Distance within which bees actively separate
BEE_MAX_VELOCITY = 0.1
BEE_MIN_VELOCITY = 0.02
BEE_MASS = 15.0             # Mass factor for force application
AVOID_EDGE_MARGIN = 5       # Distance from map edge to start avoiding
AVOID_EDGE_STRENGTH = 0.00007 # Strength of edge avoidance force
AVOID_EDGE_FORCE_MULTIPLIER = 100.0
AVOID_WATER_FORCE_MULTIPLIER = 0.8

# Background Generation
BG_NOISE_OCTAVES = 8        # Perlin noise octaves
BG_NOISE_SCALE = 4          # Zoom level for Perlin noise
BG_WATER_THRESHOLD = 130/255 # Threshold for tile to be water
BG_SAND_THRESHOLD = 120/255  # Threshold for tile to be sand
BG_COLORFUL_EXPONENT = 0.5  # Exponent to enhance brighter parts of noise map
BG_DULL_EXPONENT = 1.1      # Exponent to enhance darker parts of noise map (or make overall duller)
BG_TILE_BORDER_DARKEN_FACTOR = 0.5 # Factor to darken tile borders
BG_TILE_OUTLINE_MIN_SCALE = 8 # Minimum tile display_size (scaled) to draw outlines

# Hive
H_INITIAL_WORKERS = 50
H_INITIAL_QUEENS = 1        # (Currently unused beyond hive size calculation)
H_BEE_COOLDOWN = 3          # Frames before another bee can exit/enter hive
COMB_WIDTH, COMB_HEIGHT = 12, 9 # Dimensions of the honeycomb grid

# Hive Display (for internal view)
HIVE_DISPLAY_AREA_SIZE = 400 # Pixel size of the hive display panel
HIVE_DISPLAY_MARGIN = 10     # Margin from window edge for hive panel
HIVE_INTERNAL_GRID_UNITS = 40 # Logical grid size inside hive
HIVE_CELL_DISPLAY_SIZE = HIVE_DISPLAY_AREA_SIZE // HIVE_INTERNAL_GRID_UNITS # Pixel size of one hive grid cell

# Flowers
FLOWER_SIZE = 8 # Unscaled size of flowers

# Derived Constants / Initial mutable globals
WORLD_SIZE = INITIAL_WORLD_SIZE # Current world size, can be changed by zooming
scaled = INITIAL_WORLD_SIZE / MAP_SIZE # Pixels per grid unit

# UI
SELECTED_PANEL_WIDTH = 300
SELECTED_PANEL_HEIGHT = 170
SELECTED_HIVE_PANEL_WIDTH = HIVE_DISPLAY_AREA_SIZE + HIVE_DISPLAY_MARGIN * 2 # Match hive display
SELECTED_HIVE_PANEL_HEIGHT = HIVE_DISPLAY_AREA_SIZE + HIVE_DISPLAY_MARGIN * 2


## INITIALISATION !!!
pygame.init()
pygame.font.init() # Explicitly initialize font module
STATS_FONT = pygame.font.SysFont("Arial", 16)
np.set_printoptions(threshold=sys.maxsize) # Make print np arrays more comprehensive

# Global variables for screen, clock, camera, and map data
screen: pygame.Surface
clock: pygame.time.Clock
camera_offset: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
background_surface: pygame.Surface
map_arr: Optional[np.ndarray] = None # Holds the Perlin noise values for the map
frames: int = 0 # Global frame counter


#
# HELPER FUNCTIONS
#

def is_hovered(mouse_pos: pygame.math.Vector2, rect_pos: pygame.math.Vector2, rect_width: int, rect_height: int) -> bool:
    """Checks if the mouse is hovering over a screen-space rectangle."""
    hover_rect = pygame.Rect(rect_pos.x, rect_pos.y, rect_width, rect_height)
    return hover_rect.collidepoint(mouse_pos.x, mouse_pos.y)

def gridpos_to_screenpos(grid_pos: pygame.math.Vector2) -> pygame.math.Vector2:
    """Converts grid coordinates to screen coordinates."""
    return grid_pos * scaled - camera_offset

def screenpos_to_gridpos(screen_pos: pygame.math.Vector2) -> pygame.math.Vector2:
    """Converts screen coordinates to grid coordinates."""
    return (screen_pos + camera_offset) / scaled

def hive_internal_pos_to_screenpos(hive_internal_pos: pygame.math.Vector2) -> pygame.math.Vector2:
    """Converts internal hive grid coordinates to screen coordinates for hive view."""
    top_left_of_hive_display = pygame.math.Vector2(
        WINDOW_WIDTH - HIVE_DISPLAY_AREA_SIZE - HIVE_DISPLAY_MARGIN,
        WINDOW_HEIGHT - HIVE_DISPLAY_AREA_SIZE - HIVE_DISPLAY_MARGIN
    )
    return top_left_of_hive_display + hive_internal_pos * HIVE_CELL_DISPLAY_SIZE

def screenpos_to_hive_internal_pos(screen_pos: pygame.math.Vector2) -> pygame.math.Vector2:
    """Converts screen coordinates to internal hive grid coordinates."""
    top_left_of_hive_display = pygame.math.Vector2(
        WINDOW_WIDTH - HIVE_DISPLAY_AREA_SIZE - HIVE_DISPLAY_MARGIN,
        WINDOW_HEIGHT - HIVE_DISPLAY_AREA_SIZE - HIVE_DISPLAY_MARGIN
    )
    return (screen_pos - top_left_of_hive_display) / HIVE_CELL_DISPLAY_SIZE

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              colour: Tuple[int, int, int], position: Tuple[float, float],
              anchor: str = "topleft") -> None:
    """Draws text on a surface with a specific anchor point."""
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, position)
    surface.blit(text_surface, text_rect)

def check_camera_pan_by_mouse() -> None:
    """Pans the camera if the mouse is at the edge of the window."""
    global camera_offset
    mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
    mouse_offset_delta = pygame.math.Vector2(0, 0)

    if mouse_pos.y <= 0:
        mouse_offset_delta.y = -CAMERA_SCROLL_SPEED
    elif mouse_pos.y >= WINDOW_HEIGHT - 1:
        mouse_offset_delta.y = CAMERA_SCROLL_SPEED
    
    if mouse_pos.x <= 0:
        mouse_offset_delta.x = -CAMERA_SCROLL_SPEED
    elif mouse_pos.x >= WINDOW_WIDTH - 1:
        mouse_offset_delta.x = CAMERA_SCROLL_SPEED

    camera_offset += mouse_offset_delta

def get_sigmoid(x: float) -> float:
    """Computes the sigmoid function."""
    return 1 / (1 + math.exp(-x))

def generate_map_data(size: int) -> None:
    """Generates Perlin noise data for the map background."""
    global map_arr
    map_arr = np.zeros((size, size), dtype=float)
    x_offset = random.uniform(0, 10000)
    y_offset = random.uniform(0, 10000)
    
    for i in range(size):
        for j in range(size):
            # Generate Perlin noise, normalized to [0, 1]
            noise_val = pnoise2(
                (i + x_offset) * BG_NOISE_SCALE / size,
                (j + y_offset) * BG_NOISE_SCALE / size,
                BG_NOISE_OCTAVES
            )
            map_arr[i][j] = (noise_val + 1) / 2 # Normalize to 0-1 range

    render_background_view(size) # Initial render of the visible part

def render_background_view(size: int) -> None:
    """Renders the currently visible portion of the map background."""
    if map_arr is None:
        return

    start_col = math.floor(camera_offset.x / scaled)
    end_col = math.ceil((WINDOW_WIDTH + camera_offset.x) / scaled)
    start_row = math.floor(camera_offset.y / scaled)
    end_row = math.ceil((WINDOW_HEIGHT + camera_offset.y) / scaled)

    # Clamp to world boundaries
    start_col = max(0, start_col)
    end_col = min(size, end_col)
    start_row = max(0, start_row)
    end_row = min(size, end_row)

    for i in range(start_col, end_col):
        for j in range(start_row, end_row):
            noise_val = map_arr[i][j]
            
            # Apply exponents to adjust color intensity distribution
            val_for_dark = round(255 * (noise_val ** BG_DULL_EXPONENT))
            val_for_bright = round(255 * (noise_val ** BG_COLORFUL_EXPONENT))

            color: Tuple[int,int,int]
            if val_for_dark / 255 >= BG_WATER_THRESHOLD: # Water
                color = (255 - val_for_dark, 255 - val_for_dark, val_for_bright)
            elif BG_SAND_THRESHOLD < val_for_dark / 255 < BG_WATER_THRESHOLD: # Sand
                color = (val_for_bright, val_for_bright, val_for_dark)
            else: # Land/Grass
                color = (val_for_dark, val_for_bright, val_for_dark)
            
            border_color = (
                int(color[0] * BG_TILE_BORDER_DARKEN_FACTOR),
                int(color[1] * BG_TILE_BORDER_DARKEN_FACTOR),
                int(color[2] * BG_TILE_BORDER_DARKEN_FACTOR)
            )

            tile_screen_pos = gridpos_to_screenpos(pygame.math.Vector2(i, j))
            
            tile_rect = pygame.Rect(tile_screen_pos.x, tile_screen_pos.y, math.ceil(scaled), math.ceil(scaled)) #ceil for no gaps
            pygame.draw.rect(background_surface, color, tile_rect)

            if scaled > BG_TILE_OUTLINE_MIN_SCALE:
                pygame.draw.rect(background_surface, border_color, tile_rect, 1)

#
# CLASSES
#
class Simulation():
    def __init__(self) -> None:
        self.creatures: List['Creature'] = []
        self.hives: List['Hive'] = []
        self.flowers: List['Flower'] = []
        self.obstacles: List['Obstacle'] = []
        
        self.selected_bee: Optional['Creature'] = None
        self.selected_hive: Optional['Hive'] = None

        # Obstacle map for efficient collision or pathfinding (1 indicates obstacle)
        self.obstacle_map: np.ndarray = np.zeros((MAP_SIZE + 1, MAP_SIZE + 1))
        
    def add_creature(self, creature: 'Creature') -> None:
        self.creatures.append(creature)

    def remove_creature(self, creature: 'Creature') -> None:
        if creature in self.creatures:
            self.creatures.remove(creature)

    def add_hive(self, hive: 'Hive') -> None:
        self.hives.append(hive)

    def remove_hive(self, hive: 'Hive') -> None:
        if hive in self.hives:
            self.hives.remove(hive)

    def add_flower(self, flower: 'Flower') -> None:
        self.flowers.append(flower)

    def remove_flower(self, flower: 'Flower') -> None:
        if flower in self.flowers:
            self.flowers.remove(flower)

    def add_obstacle(self, obstacle: 'Obstacle') -> None:
        self.obstacles.append(obstacle)
        # Mark the perimeter of the obstacle on the obstacle_map
        # Assumes obstacle.pos is top-left grid coordinate
        center_x = int(obstacle.pos.x + obstacle.size / 2) # Approx center
        center_y = int(obstacle.pos.y + obstacle.size / 2)
        
        # Iterate over a square region defined by obstacle.size around its pos
        # and mark the border cells.
        # Note: This logic marks a perimeter. If filled area is needed, adjust.
        min_gx, max_gx = int(obstacle.pos.x), int(obstacle.pos.x + obstacle.size)
        min_gy, max_gy = int(obstacle.pos.y), int(obstacle.pos.y + obstacle.size)

        for gx in range(min_gx, max_gx):
            for gy in range(min_gy, max_gy):
                if 0 <= gx < MAP_SIZE and 0 <= gy < MAP_SIZE: # Bounds check
                    if gx == min_gx or gx == max_gx -1 or gy == min_gy or gy == max_gy -1:
                         self.obstacle_map[gx, gy] = 1
        
    def run(self) -> None:
        for hive in self.hives[:]: # Iterate copy for safe removal
            hive.update(self)
        for bee in self.creatures[:]:
            bee.update(self)
        for flower in self.flowers[:]:
            flower.update(self)
        for obstacle in self.obstacles[:]: 
            obstacle.update(self)
        self.show_selected_info_panel()
    
    def handle_click(self, click_pos_screen: Tuple[int, int]) -> None:
        clicked_on_something = False
        click_vec = pygame.math.Vector2(click_pos_screen)

        self.selected_bee = None
        self.selected_hive = None
        
        # Check hives first (often larger targets)
        for hive in reversed(self.hives): # Reverse for top-most
            screen_pos = gridpos_to_screenpos(hive.pos)
            # Using hive.display_size for click detection (visual representation)
            if screen_pos.distance_to(click_vec) <= hive.display_size / 2: # Assumes circular click area
                self.selected_hive = hive
                clicked_on_something = True
                print(f"Selected Hive at {hive.pos}")
                break # Found a hive

        if not clicked_on_something:
            for bee in reversed(self.creatures):
                screen_pos = gridpos_to_screenpos(bee.pos)
                if screen_pos.distance_to(click_vec) <= bee.radius:
                    self.selected_bee = bee
                    clicked_on_something = True
                    print(f"Selected Bee (Energy: {bee.energy:.2f})")
                    break # Found a bee

    def show_selected_info_panel(self) -> None:
        if not self.selected_bee and not self.selected_hive:
            return

        panel_pos = pygame.math.Vector2(10, 10)
        
        if self.selected_bee:
            panel_surface = pygame.Surface((SELECTED_PANEL_WIDTH, SELECTED_PANEL_HEIGHT), pygame.SRCALPHA)
            panel_surface.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(panel_surface, panel_pos)

            bee = self.selected_bee
            stats: Dict[str, Any] = {
                "Position": bee.pos,
                "Velocity": bee.velocity,
                "Energy": bee.energy,
                "Honey": bee.honey,
                "Seeking Honey?": bee.seeking_honey,
                "Closest Flower": bee.closest_flower.pos if bee.closest_flower else "N/A",
                "Colour": bee.colour,
            }
            
            y_offset = panel_pos.y + 10 # Start text inside panel
            for key, value in stats.items():
                display_value: str
                if isinstance(value, pygame.math.Vector2):
                    display_value = f"({value.x:.2f}, {value.y:.2f})"
                elif isinstance(value, float):
                    display_value = f"{value:.2f}"
                else:
                    display_value = str(value)
                text_to_draw = f"{key}: {display_value}"
                draw_text(screen, text_to_draw, STATS_FONT, TEXT_COLOUR, (panel_pos.x + 10, y_offset))
                y_offset += 20

        elif self.selected_hive:
            # Hive panel appears on the right
            hive_panel_pos = pygame.math.Vector2(
                WINDOW_WIDTH - SELECTED_HIVE_PANEL_WIDTH - HIVE_DISPLAY_MARGIN,
                WINDOW_HEIGHT - SELECTED_HIVE_PANEL_HEIGHT - HIVE_DISPLAY_MARGIN
            )
            panel_surface = pygame.Surface((SELECTED_HIVE_PANEL_WIDTH, SELECTED_HIVE_PANEL_HEIGHT), pygame.SRCALPHA)
            panel_surface.fill((50, 25, 0, 220)) # Brownish, semi-transparent
            screen.blit(panel_surface, hive_panel_pos)
            
            # Draw hive name/stats
            draw_text(screen, f"Hive Interior (Honey View)", STATS_FONT, TEXT_COLOUR,
                      (hive_panel_pos.x + 10, hive_panel_pos.y + 10))

            # Draw combs
            comb_idx = 0
            for r in range(COMB_HEIGHT):
                for c in range(COMB_WIDTH):
                    honey_amount = self.selected_hive.combs_honey[r, c]
                    if honey_amount >= 0: # Valid comb
                        comb_center_in_hive_units = pygame.math.Vector2(self.selected_hive.combs_layout[comb_idx])
                        screen_comb_pos = hive_internal_pos_to_screenpos(comb_center_in_hive_units)
                        
                        # Color based on honey amount (0-100)
                        # Hue: Yellow (60) to Orange (30) as honey fills up
                        # Saturation: Increases with honey
                        # Lightness: Increases with honey
                        hue = 60 - (honey_amount / 100) * 30 # 60 (yellow) down to 30 (orange)
                        saturation = 50 + (honey_amount / 100) * 50
                        lightness = 20 + (honey_amount / 100) * 30
                        
                        comb_color = pygame.Color(0)
                        comb_color.hsla = (hue, saturation, lightness, 100)
                        
                        pygame.draw.circle(screen, comb_color, screen_comb_pos, HIVE_CELL_DISPLAY_SIZE * 0.45) # Slightly smaller than cell
                    comb_idx += 1
            
            # Draw bees inside the hive
            for bee in self.selected_hive.bees_inside:
                bee.draw_inside_hive()

class Flower():
    def __init__(self, x: float, y: float):
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(x, y)
        self.size_unscaled: float = FLOWER_SIZE # Base size, scaling handled by 'scaled' global
        self.petal_color: Tuple[int, int, int] = (random.randint(200, 255), random.randint(100,200), random.randint(200,255)) # Example: Pink/Purple shades
        self.pollen: float = 100.0
        # self.angle = 0 (Unused)
        # self.rotspeed = 0.005 (Unused)
    
    def update(self, manager: Simulation) -> None:
        self.draw()
        if self.pollen <= 0:
            manager.remove_flower(self)
            # print(f"Flower at {self.pos} depleted.") # Less intrusive print

    def draw(self) -> None:
        screen_pos = gridpos_to_screenpos(self.pos)
        # Simplified drawing: a circle representing the flower
        pygame.draw.circle(screen, self.petal_color, screen_pos, self.size_unscaled * scaled * 0.125) # FLOWER_SIZE is large, adjust factor


class Obstacle():
    def __init__(self, x: float, y: float):
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(x, y) # Top-left in grid units
        self.size: int = random.randint(1, 3) # Size in grid units (e.g., 2x2 grid obstacle)
        self.color: Tuple[int, int, int] = (80, 80, 80)

        # Bounding box in grid units
        self.min_x: float = self.pos.x
        self.min_y: float = self.pos.y
        self.max_x: float = self.pos.x + self.size
        self.max_y: float = self.pos.y + self.size

    def update(self, manager: Simulation) -> None:
        self.draw()

    def get_closest_point_on_bounds(self, obj_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Returns the closest point on the obstacle's AABB to obj_pos."""
        closest_point = pygame.math.Vector2()
        closest_point.x = max(self.min_x, min(obj_pos.x, self.max_x))
        closest_point.y = max(self.min_y, min(obj_pos.y, self.max_y))
        return closest_point
        
    def draw(self) -> None:
        screen_pos = gridpos_to_screenpos(self.pos)
        # Obstacle is 'self.size' grid units wide and tall
        pygame.draw.rect(screen, self.color, 
                         (screen_pos.x, screen_pos.y, 
                          scaled * self.size, scaled * self.size))


class Hive():
    def __init__(self, x: float, y: float, sim_manager: Simulation):
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(x, y) # Center of the hive in grid units

        self.workers_pop: int = H_INITIAL_WORKERS
        self.queen_pop: int = H_INITIAL_QUEENS # (Currently mostly for initial size)
        
        self.bees_inside: List['Creature'] = []
        self.bees_outside: List['Creature'] = []
        
        self.internal_cooldown: int = 0 # Cooldown for bees exiting
        self.next_bee_to_check_idx: int = 0 # Index for cycling through bees_inside

        # Visual representation size on the main map
        self.display_size: float = scaled * 4 # Example: 4 grid units wide visually

        for _ in range(self.workers_pop):
            # Bees start at the hive's world position, but will be managed by hive logic
            temp_bee = Creature(self.pos.x, self.pos.y, self)
            sim_manager.add_creature(temp_bee) # Add to simulation
            self.bees_inside.append(temp_bee)   # Initially all bees are inside

        # Honeycomb layout (positions within the HIVE_INTERNAL_GRID_UNITS)
        self.combs_layout: List[Tuple[float, float]] = [] # Store (x,y) for each comb center
        self.combs_honey: np.ndarray = np.zeros((COMB_HEIGHT, COMB_WIDTH)) # Honey per comb

        # --- Honeycomb generation (for HIVE_INTERNAL_GRID_UNITS coordinate system) ---
        # These are parameters for hexagonal packing within the hive display area
        comb_radius_pixels = HIVE_CELL_DISPLAY_SIZE * 0.4 # visual radius for drawing, not for layout logic here
        
        # Using simpler grid layout for comb logic, hex for display drawing
        cell_w = HIVE_INTERNAL_GRID_UNITS / COMB_WIDTH
        cell_h = HIVE_INTERNAL_GRID_UNITS / COMB_HEIGHT
        
        start_x = cell_w / 2
        start_y = cell_h / 2

        for r in range(COMB_HEIGHT):
            y_pos = start_y + r * cell_h
            current_offset_x = start_x
            if r % 2 != 0: # Offset every other row for hexagonal feel if desired
                current_offset_x += cell_w / 2
                 # Ensure it doesn't go out of bounds if COMB_WIDTH is small
                if COMB_WIDTH == 1: current_offset_x = start_x

            for c in range(COMB_WIDTH):
                x_pos = current_offset_x + c * cell_w
                if r % 2 != 0 and x_pos >= HIVE_INTERNAL_GRID_UNITS - cell_w/2 and COMB_WIDTH > 1: # If row is offset and this cell would be too far
                    self.combs_layout.append((-1,-1)) # Invalid placeholder
                    self.combs_honey[r,c] = -1 # Mark as unusable
                    continue

                self.combs_layout.append((x_pos, y_pos))
                self.combs_honey[r, c] = 0 # Initial honey

                # Example: Make some edge combs unusable (simplified from original)
                # This logic should be refined if a specific pattern is desired.
                is_edge_comb = (r == 0 or r == COMB_HEIGHT - 1 or c == 0 or c == COMB_WIDTH - 1)
                is_corner_comb = (r==0 and c==0) or (r==0 and c==COMB_WIDTH-1) or \
                                 (r==COMB_HEIGHT-1 and c==0) or (r==COMB_HEIGHT-1 and c==COMB_WIDTH-1)
                if is_corner_comb or (is_edge_comb and random.random() < 0.3): # Make corners and some edges unusable
                     # self.combs_honey[r,c] = -1 # Mark as unusable
                     # self.combs_layout[-1] = (-1,-1) # Also mark layout as invalid for this
                     pass # For now, enable all for simplicity. Original had complex rules.
        # print("Hive Combs Honey Initial:\n", self.combs_honey)


    def update(self, manager: Simulation) -> None:
        self.display_size = scaled * 4 # Update visual size if 'scaled' changes

        if self.internal_cooldown == 0 and len(self.bees_inside) > 0:
            if self.next_bee_to_check_idx >= len(self.bees_inside):
                self.next_bee_to_check_idx = 0 # Reset index

            if not self.bees_inside: return # No bees to process

            bee_to_consider = self.bees_inside[self.next_bee_to_check_idx]
            
            if bee_to_consider.seeking_honey:
                # Move bee from inside to outside
                self.bees_inside.pop(self.next_bee_to_check_idx)
                self.bees_outside.append(bee_to_consider)
                bee_to_consider.pos = self.pos.copy() # Emerge at hive's world location
                self.internal_cooldown = H_BEE_COOLDOWN
                # Don't increment index here, list shrinks
            else:
                self.next_bee_to_check_idx += 1
        
        elif self.internal_cooldown > 0:
            self.internal_cooldown -= 1

        self.draw()

    def draw(self) -> None:
        screen_pos = gridpos_to_screenpos(self.pos)
        # Draws the hive with its center at self.pos
        hive_rect = pygame.Rect(0,0, self.display_size, self.display_size)
        hive_rect.center = (screen_pos.x, screen_pos.y)
        pygame.draw.rect(screen, (200, 150, 0), hive_rect) # Brownish yellow


class Creature(): # Represents a Bee
    def __init__(self, x: float, y: float, hive: Hive):
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(x, y) # World position
        self.hive_pos: pygame.math.Vector2 = pygame.math.Vector2(
            random.uniform(0, HIVE_INTERNAL_GRID_UNITS), 
            random.uniform(0, HIVE_INTERNAL_GRID_UNITS)
        ) # Position inside the hive's internal grid
        
        self.energy: float = CR_INITIAL_ENERGY
        self.honey: float = 0.0
        self.hive: Hive = hive

        self.velocity: pygame.math.Vector2 = pygame.math.Vector2(BEE_MIN_VELOCITY, 0).rotate(random.uniform(0, 360))
        self.acceleration: pygame.math.Vector2 = pygame.math.Vector2()
        self.speed: float = self.velocity.length()

        self.colour: Tuple[int, int, int] = (random.randint(200,255), random.randint(200,255), random.randint(0,50)) # Yellowish
        self.seeking_honey: bool = True
        self.closest_flower: Optional[Flower] = None 
        
        # Stagger calculations for performance
        self.update_frame_offset: int = random.randint(0, 4) 

        # Dynamic properties based on energy/scale
        self.size_raw: float = self.energy / 500 # Base size factor
        self.size_scaled: float = self.size_raw * scaled # Visual size on screen
        self.radius: float = self.size_scaled + 2 # Click/interaction radius

        self.is_selected: bool = False # For drawing highlights

    def update(self, manager: Simulation) -> None:
        global frames # Use global frame counter
        
        is_outside_hive = self in self.hive.bees_outside

        steering_force = pygame.math.Vector2()

        if is_outside_hive:
            # --- Behavior when outside the hive ---
            self.avoid_world_bounds_hard() # Hard clamp to prevent escaping map

            # More complex calculations less frequently
            if frames % 5 == self.update_frame_offset:
                steering_force += self.calculate_boid_forces(self.hive.bees_outside, self.pos)
                steering_force += self.calculate_avoid_edge_force(self.pos, 0, MAP_SIZE) * AVOID_EDGE_FORCE_MULTIPLIER
                steering_force += self.calculate_obstacle_avoidance(self.pos, manager.obstacles)
                if map_arr is not None:
                     steering_force += self.calculate_water_avoidance(map_arr) * AVOID_WATER_FORCE_MULTIPLIER
            
            self.update_flower_seeking_logic(manager.flowers)
            
        else: # Inside the hive
            self.avoid_hive_bounds_hard() # Hard clamp for internal hive movement
            if frames % 5 == self.update_frame_offset: # Boids inside hive too
                 steering_force += self.calculate_boid_forces(self.hive.bees_inside, self.hive_pos)
                 steering_force += self.calculate_avoid_edge_force(self.hive_pos, 0, HIVE_INTERNAL_GRID_UNITS) * AVOID_EDGE_FORCE_MULTIPLIER # Use smaller multiplier for hive

            if not self.seeking_honey:
                steering_force += self.process_honey_deposit()


        self.apply_force(steering_force)
        self.velocity += self.acceleration
        self.acceleration *= 0 # Reset acceleration

        # Add some randomness to movement
        random_turn_angle = (random.random() - 0.5) * 30 # Degrees
        self.velocity.rotate_ip(random_turn_angle)
        
        self.speed = self.velocity.length()
        if self.speed > BEE_MAX_VELOCITY:
            self.velocity.scale_to_length(BEE_MAX_VELOCITY)
        elif self.speed > 0 and self.speed < BEE_MIN_VELOCITY : # Avoid zero division if speed is 0
             self.velocity.scale_to_length(BEE_MIN_VELOCITY)
        self.speed = self.velocity.length() # Update speed after clamping

        if is_outside_hive:
            self.pos += self.velocity
        else: # Moving within hive_pos
            self.hive_pos += self.velocity
        
        # Update status based on energy/honey
        self.update_state() 

        if frames % FPS == 0: # Every second
            self.energy -= CR_ENERGY_DECAY

        if self.energy <= 0:
            # print(f"Bee ran out of energy at {self.pos}.")
            if is_outside_hive:
                self.hive.bees_outside.remove(self)
            elif self in self.hive.bees_inside: # Should not happen if it's seeking honey to exit
                self.hive.bees_inside.remove(self)
            manager.remove_creature(self)
            return # Bee is gone

        # Update visual size properties
        self.size_raw = max(0.1, self.energy / 500) # Ensure minimum size
        self.size_scaled = self.size_raw * scaled
        self.radius = self.size_scaled + 2

        self.is_selected = (manager.selected_bee == self)

        if is_outside_hive:
            self.draw_on_map()

    def apply_force(self, force: pygame.math.Vector2) -> None:
        if BEE_MASS > 0: # Avoid division by zero
            self.acceleration += force / BEE_MASS

    def update_state(self) -> None:
        """Manages transitions like 'full of honey' -> 'return to hive'."""
        min_honey_to_return = 80
        if self.honey >= min_honey_to_return:
            self.seeking_honey = False
        # Could add: if energy low and has honey, return. If energy low and no honey, seek flower more desperately.
    
    def update_flower_seeking_logic(self, flowers: List[Flower]) -> None:
        if not flowers: # No flowers to seek
            self.closest_flower = None
            # Potentially add wandering behavior here
            return

        # Find closest flower
        if not self.closest_flower or self.closest_flower.pollen <= 0 or self.closest_flower not in flowers:
            min_dist_sq = float('inf')
            for flower in flowers:
                if flower.pollen > 0:
                    dist_sq = self.pos.distance_squared_to(flower.pos)
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        self.closest_flower = flower
        
        if not self.closest_flower: return # Still no valid flower

        if self.seeking_honey:
            self.steer_towards_target(self.closest_flower.pos)
            # Collect honey if close enough
            if self.pos.distance_to(self.closest_flower.pos) <= BEE_DETECTION_RADIUS / 2: # Closer interaction
                pollen_taken = 0.5
                actual_taken = min(pollen_taken, self.closest_flower.pollen)
                self.honey += actual_taken
                self.closest_flower.pollen -= actual_taken
        else: # Not seeking honey, so return to hive
            self.steer_towards_target(self.hive.pos)
            # Check for hive entry
            if self.pos.distance_to(self.hive.pos) <= BEE_DETECTION_RADIUS * 1.5: # Larger radius to 'find' hive
                self.attempt_enter_hive()
    
    def steer_towards_target(self, target_pos: pygame.math.Vector2, slowing_radius: float = BEE_DETECTION_RADIUS * 2) -> None:
        """Steers the bee towards a target position, optionally slowing down."""
        desired_velocity = target_pos - self.pos
        dist_to_target = desired_velocity.length()

        if dist_to_target > 0:
            if dist_to_target < slowing_radius: # Arrive behavior
                desired_velocity.scale_to_length(self.speed * (dist_to_target / slowing_radius))
            else:
                desired_velocity.scale_to_length(self.speed) # Max speed
            
            steer = desired_velocity - self.velocity
            # Limit steer force if needed (e.g., steer.scale_to_length(MAX_STEER_FORCE))
            self.apply_force(steer)

    def attempt_enter_hive(self) -> None:
        if self in self.hive.bees_outside: # Ensure it's actually outside
            self.hive.bees_inside.append(self)
            self.hive.bees_outside.remove(self)
            # Reset some properties for hive life
            self.hive_pos = pygame.math.Vector2(random.uniform(0, HIVE_INTERNAL_GRID_UNITS), 
                                                random.uniform(0, HIVE_INTERNAL_GRID_UNITS))
            self.velocity = pygame.math.Vector2(BEE_MIN_VELOCITY/2, 0).rotate(random.uniform(0,360)) # Slower inside

    def calculate_boid_forces(self, group: List['Creature'], current_pos_type: pygame.math.Vector2) -> pygame.math.Vector2:
        """Calculates separation, alignment, and cohesion forces."""
        total_force = pygame.math.Vector2()
        total_force += self.separation(group, current_pos_type) * 1.5 # Stronger separation
        total_force += self.alignment(group, current_pos_type) * 1.0
        total_force += self.cohesion(group, current_pos_type) * 1.0
        return total_force * 1.2 # Overall boid behavior strength

    def calculate_obstacle_avoidance(self, current_pos: pygame.math.Vector2, obstacles: List[Obstacle]) -> pygame.math.Vector2:
        avoidance_force = pygame.math.Vector2()
        for rock in obstacles:
            closest_point_on_rock = rock.get_closest_point_on_bounds(current_pos)
            diff_vec = current_pos - closest_point_on_rock
            dist_mag = diff_vec.length()

            if 0 < dist_mag < BEE_SEPARATION_THRESHOLD * 1.5: # Slightly larger threshold for rocks
                # Force is stronger closer to the obstacle
                strength = (BEE_SEPARATION_THRESHOLD * 1.5 - dist_mag) / (BEE_SEPARATION_THRESHOLD * 1.5)
                avoidance_force += diff_vec.normalize() * strength * 0.1 # Adjust multiplier as needed
        return avoidance_force

    def calculate_water_avoidance(self, current_map_arr: np.ndarray) -> pygame.math.Vector2:
        avoidance_force = pygame.math.Vector2()
        if self.speed == 0:
            return avoidance_force
        
        # Look ahead based on velocity
        look_ahead_dist = BEE_DETECTION_RADIUS / 2 
        look_ahead_pos = self.pos + self.velocity.normalize() * look_ahead_dist
        
        # Clamp to map bounds and convert to int for array indexing
        map_x = int(max(0, min(look_ahead_pos.x, MAP_SIZE - 1)))
        map_y = int(max(0, min(look_ahead_pos.y, MAP_SIZE - 1)))

        if current_map_arr[map_x, map_y] >= BG_WATER_THRESHOLD:
            # Steer away from water tile: force perpendicular to current velocity, or directly away
            # A simple approach: steer directly away from the look_ahead_pos if it's water
            avoidance_force -= (look_ahead_pos - self.pos).normalize() * 0.05 # Adjust strength
        return avoidance_force
    
    def calculate_avoid_edge_force(self, current_pos: pygame.math.Vector2, min_bound: float, max_bound: float) -> pygame.math.Vector2:
        """Calculates force to steer away from boundaries."""
        force = pygame.math.Vector2()
        
        if current_pos.x <= min_bound + AVOID_EDGE_MARGIN:
            force.x += AVOID_EDGE_STRENGTH * (AVOID_EDGE_MARGIN - (current_pos.x - min_bound))
        elif current_pos.x >= max_bound - AVOID_EDGE_MARGIN:
            force.x -= AVOID_EDGE_STRENGTH * (AVOID_EDGE_MARGIN - (max_bound - current_pos.x))

        if current_pos.y <= min_bound + AVOID_EDGE_MARGIN:
            force.y += AVOID_EDGE_STRENGTH * (AVOID_EDGE_MARGIN - (current_pos.y - min_bound))
        elif current_pos.y >= max_bound - AVOID_EDGE_MARGIN:
            force.y -= AVOID_EDGE_STRENGTH * (AVOID_EDGE_MARGIN - (max_bound - current_pos.y))
        return force

    def avoid_world_bounds_hard(self) -> None:
        """Hard clamps position to world map boundaries."""
        self.pos.x = max(0, min(self.pos.x, MAP_SIZE - 0.01)) # -0.01 to avoid exact edge for array indexing
        self.pos.y = max(0, min(self.pos.y, MAP_SIZE - 0.01))

    def avoid_hive_bounds_hard(self) -> None:
        """Hard clamps position to hive internal boundaries."""
        self.hive_pos.x = max(0, min(self.hive_pos.x, HIVE_INTERNAL_GRID_UNITS - 0.01))
        self.hive_pos.y = max(0, min(self.hive_pos.y, HIVE_INTERNAL_GRID_UNITS - 0.01))

    def separation(self, group: List['Creature'], own_current_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        sep_force = pygame.math.Vector2()
        for other_bee in group:
            if other_bee is self:
                continue
            
            # Determine if we are comparing world positions or hive internal positions
            other_pos = other_bee.pos if self in self.hive.bees_outside else other_bee.hive_pos
            
            dist = own_current_pos.distance_to(other_pos)
            if 0 < dist < BEE_SEPARATION_THRESHOLD:
                # Force is inversely proportional to distance
                diff = own_current_pos - other_pos
                sep_force += diff.normalize() / dist # Stronger repulsion when closer
        return sep_force

    def alignment(self, group: List['Creature'], own_current_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        avg_velocity = pygame.math.Vector2()
        neighbor_count = 0
        for other_bee in group:
            if other_bee is self:
                continue
            other_pos = other_bee.pos if self in self.hive.bees_outside else other_bee.hive_pos
            if own_current_pos.distance_to(other_pos) < BEE_DETECTION_RADIUS:
                avg_velocity += other_bee.velocity
                neighbor_count += 1
        
        if neighbor_count > 0:
            avg_velocity /= neighbor_count
            if avg_velocity.length_squared() > 0: # Check if not zero vector
                 # Steer towards average velocity
                desired_steer = avg_velocity.normalize() * self.speed - self.velocity
                return desired_steer
        return pygame.math.Vector2()

    def cohesion(self, group: List['Creature'], own_current_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        center_of_mass = pygame.math.Vector2()
        neighbor_count = 0
        for other_bee in group:
            if other_bee is self:
                continue
            other_pos = other_bee.pos if self in self.hive.bees_outside else other_bee.hive_pos
            if own_current_pos.distance_to(other_pos) < BEE_DETECTION_RADIUS:
                center_of_mass += other_pos
                neighbor_count += 1

        if neighbor_count > 0:
            center_of_mass /= neighbor_count
            desired_direction = center_of_mass - own_current_pos
            if desired_direction.length_squared() > 0:
                # Steer towards center of mass
                desired_steer = desired_direction.normalize() * self.speed - self.velocity
                return desired_steer
        return pygame.math.Vector2()
        
    def draw_on_map(self) -> None:
        """Draws the bee on the main game map."""
        screen_pos = gridpos_to_screenpos(self.pos)
        pygame.draw.circle(screen, self.colour, screen_pos, self.radius) 
        if self.is_selected:
            pygame.draw.circle(screen, CR_HOVER_COLOUR, screen_pos, self.radius + 2, 2) # Selection highlight
            # Debug radii
            pygame.draw.circle(screen, CR_HOVER_COLOUR, screen_pos, BEE_DETECTION_RADIUS * scaled, 1) 
            pygame.draw.circle(screen, (255,0,0), screen_pos, BEE_SEPARATION_THRESHOLD * scaled, 1)

    def process_honey_deposit(self) -> pygame.math.Vector2:
        """Bee logic for finding a comb and depositing honey when inside the hive."""
        if self.honey <= 0:
            self.seeking_honey = True # Run out of honey, go seek more
            # No need to try entering hive, already inside. Will exit on next hive update.
            return pygame.math.Vector2()

        target_comb_pos_hive_units: Optional[pygame.math.Vector2] = None
        target_comb_indices: Optional[Tuple[int, int]] = None # (row, col)

        # Find the first available comb to deposit honey
        # Iterate through combs_honey to find a non-full, valid comb
        for r in range(COMB_HEIGHT):
            for c in range(COMB_WIDTH):
                if 0 <= self.hive.combs_honey[r, c] < 100: # Valid and not full
                    flat_idx = r * COMB_WIDTH + c
                    if flat_idx < len(self.hive.combs_layout) and self.hive.combs_layout[flat_idx] != (-1,-1):
                        target_comb_pos_hive_units = pygame.math.Vector2(self.hive.combs_layout[flat_idx])
                        target_comb_indices = (r,c)
                        break
            if target_comb_pos_hive_units:
                break
        
        if target_comb_pos_hive_units and target_comb_indices:
            dist_to_comb = self.hive_pos.distance_to(target_comb_pos_hive_units)
            if dist_to_comb <= HIVE_CELL_DISPLAY_SIZE * 0.2: # Close enough to deposit
                deposit_amount = 0.1
                actual_deposit = min(deposit_amount, self.honey, 100 - self.hive.combs_honey[target_comb_indices])
                
                self.honey -= actual_deposit
                self.hive.combs_honey[target_comb_indices] += actual_deposit
                return pygame.math.Vector2() # Stay put while depositing
            else:
                # Steer towards the comb
                direction_to_comb = target_comb_pos_hive_units - self.hive_pos
                if direction_to_comb.length_squared() > 0:
                     # Simpler steering for inside hive: just move towards it
                    return direction_to_comb.normalize() * 0.01 # Gentle force
        
        return pygame.math.Vector2() # No target or already depositing

    def draw_inside_hive(self) -> None:
        """Draws the bee inside the hive view panel."""
        screen_pos = hive_internal_pos_to_screenpos(self.hive_pos)
        # Smaller representation inside hive
        pygame.draw.circle(screen, self.colour, screen_pos, max(2, self.energy / 20)) 


# Global simulation instance
sim_manager = Simulation()

def add_initial_game_objects() -> None:
    """Adds initial hives, flowers, and obstacles to the simulation."""
    if map_arr is None:
        print("Error: Map data not generated before adding objects.")
        return

    occupied_coords: List[pygame.math.Vector2] = []

    def get_valid_spawn_coord() -> Optional[pygame.math.Vector2]:
        for _ in range(100): # Try 100 times to find a spot
            coord = pygame.math.Vector2(
                random.randint(OBJECT_SPAWN_MARGIN, MAP_SIZE - 1 - OBJECT_SPAWN_MARGIN),
                random.randint(OBJECT_SPAWN_MARGIN, MAP_SIZE - 1 - OBJECT_SPAWN_MARGIN)
            )
            # Check if on water or already occupied (simple check, not accounting for object size)
            if map_arr[int(coord.x), int(coord.y)] < BG_WATER_THRESHOLD and coord not in occupied_coords:
                occupied_coords.append(coord)
                return coord
        return None # Could not find a spot

    # Add Hives
    for _ in range(2): # Example: 2 hives
        pos = get_valid_spawn_coord()
        if pos:
            sim_manager.add_hive(Hive(pos.x, pos.y, sim_manager))

    # Add Flowers
    for _ in range(50): # Example: 50 flowers
        pos = get_valid_spawn_coord()
        if pos:
            sim_manager.add_flower(Flower(pos.x, pos.y))

    # Add Obstacles
    for _ in range(N_OBSTACLES):
        pos = get_valid_spawn_coord()
        if pos:
            sim_manager.add_obstacle(Obstacle(pos.x, pos.y))


def main() -> None:
    global screen, clock, background_surface, camera_offset, WORLD_SIZE, scaled, frames

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    pygame.event.set_grab(True) # Confine mouse to window

    background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    generate_map_data(MAP_SIZE)
    add_initial_game_objects()
    
    running = True
    while running:
        frames += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False # Allow escape to quit
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS: # Zoom in
                    WORLD_SIZE = min(WORLD_SIZE * 2, 16384 * 2) # Allow more zoom
                    scaled = WORLD_SIZE / MAP_SIZE
                if event.key == pygame.K_MINUS: # Zoom out
                    WORLD_SIZE = max(MAP_SIZE * 8, WORLD_SIZE / 2) # Min scaled tile size reasonable
                    scaled = WORLD_SIZE / MAP_SIZE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    sim_manager.handle_click(event.pos)
        
        # Camera Updates
        check_camera_pan_by_mouse()
        camera_offset.x = max(0, min(camera_offset.x, WORLD_SIZE - WINDOW_WIDTH))
        camera_offset.y = max(0, min(camera_offset.y, WORLD_SIZE - WINDOW_HEIGHT))
        
        # Background Rendering
        background_surface.fill(BACKGROUND_FILL) # Clear portion for dynamic background
        render_background_view(MAP_SIZE)

        # Main Screen Drawing
        screen.fill(BACKGROUND_FILL) # Fallback color
        screen.blit(background_surface, (0,0)) # Blit the rendered background view
        
        # Simulation Update and Draw
        sim_manager.run()

        pygame.display.flip()
        clock.tick(FPS)
        pygame.display.set_caption(f"Bee Simulation | FPS: {clock.get_fps():.2f} | Scale: {scaled:.2f} | Bees: {len(sim_manager.creatures)}")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
