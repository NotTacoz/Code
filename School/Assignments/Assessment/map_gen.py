import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
# Optional: for Gaussian blur
# from scipy.ndimage import gaussian_filter

# --- Configuration ---
MAP_SIZE = 128
RANDOM_SEED = 42  # For reproducible results. Change for different maps.

# Terrain thresholds (values from 0 to 1 from your CSV)
WATER_THRESHOLD = 130 / 255.0  # approx 0.5098
SAND_THRESHOLD = 120 / 255.0   # approx 0.4706

# Colors for plotting
GRASS_COLOR = '#2E7D32'  # Darker Green
SAND_COLOR = '#FFF176'   # Pale Yellow
WATER_COLOR = '#1565C0'  # Darker Blue
TERRAIN_COLORS = [GRASS_COLOR, SAND_COLOR, WATER_COLOR]
TERRAIN_LABELS = ['Grass', 'Sand', 'Water']

# Generation parameters (tweak these for different map styles)
NOISE_STRENGTH = 0.35       # How much randomness to add (0.0 to ~0.5 is reasonable)
CENTRAL_FEATURE_SCALE = 0.6 # Relative size of the central feature (e.g. 0.6 = 60% of half_size)
USE_GAUSSIAN_BLUR = True   # Set to True to smooth the quadrant (requires scipy)
BLUR_SIGMA = 1.5            # Sigma for Gaussian blur (if used); higher = more blur

# --- 1. Generate Symmetrical Map Data (Values 0-1) ---
def generate_symmetrical_map_data(size=MAP_SIZE, seed=RANDOM_SEED):
    """
    Generates a 2D numpy array with values between 0 and 1,
    designed to be symmetrical and visually interesting.
    """
    if seed is not None:
        np.random.seed(seed)
    
    half_size = size // 2
    
    # Create a base for the top-left quadrant
    y_coords, x_coords = np.ogrid[:half_size, :half_size] # Grid coordinates for the quadrant

    # a) Radial gradient: values decrease from the quadrant's (0,0) corner outwards.
    # This (0,0) corner will become the center of the full map.
    dist_from_quad_center = np.sqrt(x_coords**2 + y_coords**2)
    
    # Scale distances to control the size of the central feature.
    # A feature_radius where values transition from high to low.
    feature_radius = half_size * CENTRAL_FEATURE_SCALE
    
    # Create base values: high (near 1) at center, falling to 0.
    # This example creates a central "high-value" area, good for water.
    quadrant_base = np.clip(1.0 - (dist_from_quad_center / feature_radius), 0, 1)
    
    # b) Add noise for irregularity
    # Noise range from -NOISE_STRENGTH to +NOISE_STRENGTH
    random_noise = (np.random.rand(half_size, half_size) * 2 - 1) * NOISE_STRENGTH
    
    quadrant_values = np.clip(quadrant_base + random_noise, 0, 1)

    # c) Optional: Apply Gaussian blur for smoother, more organic features
    if USE_GAUSSIAN_BLUR:
        try:
            from scipy.ndimage import gaussian_filter
            quadrant_values = gaussian_filter(quadrant_values, sigma=BLUR_SIGMA)
            # Ensure values stay in [0,1] after blur (blur can sometimes push slightly outside)
            quadrant_values = np.clip(quadrant_values, 0, 1)
        except ImportError:
            print("Warning: scipy.ndimage not found. Skipping Gaussian blur.")
            print("You can install it with: pip install scipy")

    # d) Assemble the full map using symmetry
    full_map = np.zeros((size, size))
    
    full_map[:half_size, :half_size] = quadrant_values                 # Top-left
    full_map[:half_size, half_size:] = np.fliplr(quadrant_values)      # Top-right
    full_map[half_size:, :] = np.flipud(full_map[:half_size, :])     # Bottom (reflects top half)
    
    return full_map

# --- 2. Categorize Data into Terrain Types ---
def categorize_terrain(data_values):
    """
    Categorizes the data (0-1) into terrain types (0: Grass, 1: Sand, 2: Water).
    """
    # Initialize all as Grass (0)
    terrain_map_numeric = np.zeros_like(data_values, dtype=int) 
    
    # Values for Sand (1)
    is_sand = (data_values > SAND_THRESHOLD) & (data_values <= WATER_THRESHOLD)
    terrain_map_numeric[is_sand] = 1
    
    # Values for Water (2)
    is_water = data_values > WATER_THRESHOLD
    terrain_map_numeric[is_water] = 2
    
    return terrain_map_numeric

# --- 3. Plot the Map ---
def plot_terrain_map(terrain_map_numeric, colors, labels, map_size_disp):
    """
    Plots the categorized terrain map using specified colors.
    """
    cmap = matplotlib.colors.ListedColormap(colors)
    # Boundaries for discrete colors: Grass (0), Sand (1), Water (2)
    bounds = [-0.5, 0.5, 1.5, 2.5] 
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    plt.figure(figsize=(10, 10))
    im = plt.imshow(terrain_map_numeric, cmap=cmap, norm=norm, interpolation='nearest')
    
    plt.title(f'Generated Symmetrical Map ({map_size_disp}x{map_size_disp})', fontsize=16)
    plt.xticks([])
    plt.yticks([])
    
    # Colorbar
    # Create a new Axes for the colorbar, to have more control.
    cbar_ax = plt.gcf().add_axes([0.92, 0.15, 0.03, 0.7]) # [left, bottom, width, height]
    cbar = plt.colorbar(im, cax=cbar_ax, ticks=[0, 1, 2], spacing='proportional')
    cbar.ax.set_yticklabels(labels)
    cbar.set_label('Terrain Type', rotation=270, labelpad=20, fontsize=12)
    
    plt.subplots_adjust(right=0.9) # Adjust main plot to make space for colorbar
    plt.show()

# --- 4. Save to CSV ---
def save_to_csv(data_values, filename="generated_map_values.csv"):
    """Saves the raw map data (0-1 values) to a CSV file."""
    np.savetxt(filename, data_values, delimiter=',', fmt='%.4f')
    print(f"Raw map data (values 0-1) saved to {filename}")

# --- Main Execution ---
if __name__ == "__main__":
    print("Generating map data...")
    # Generate the symmetrical raw data (0-1 values)
    raw_map_data = generate_symmetrical_map_data(MAP_SIZE, seed=RANDOM_SEED)
    
    # Save the generated raw data to a CSV, as per your input format
    csv_filename = "symmetrical_map_data.csv"
    save_to_csv(raw_map_data, csv_filename)
    print(f"This CSV ('{csv_filename}') can be used as input for your existing code.")

    # --- The following part is for direct visualization ---
    # If you want to load a CSV (e.g., the one just saved, or your own):
    # print(f"\nAttempting to load map data from '{csv_filename}' for visualization...")
    # try:
    #     # Replace csv_filename with your actual input file if different
    #     loaded_raw_map_data = np.genfromtxt(csv_filename, delimiter=',')
    #     if loaded_raw_map_data.shape != (MAP_SIZE, MAP_SIZE):
    #         print(f"Warning: Loaded CSV is {loaded_raw_map_data.shape}, expected ({MAP_SIZE},{MAP_SIZE}).")
    #         # Decide how to handle: error, resize, or use loaded shape
    #         # For this example, we'll proceed but visualization might be off
    #     map_data_to_visualize = loaded_raw_map_data
    #     current_map_size_disp = loaded_raw_map_data.shape[0]
    # except IOError:
    #     print(f"Error loading CSV '{csv_filename}'. Visualizing the directly generated data instead.")
    #     map_data_to_visualize = raw_map_data
    #     current_map_size_disp = MAP_SIZE
    
    # For this script, let's directly use the generated data for visualization:
    map_data_to_visualize = raw_map_data
    current_map_size_disp = MAP_SIZE


    print("\nCategorizing terrain...")
    terrain_categories = categorize_terrain(map_data_to_visualize)
    
    print("Plotting map...")
    plot_terrain_map(terrain_categories, TERRAIN_COLORS, TERRAIN_LABELS, current_map_size_disp)

    print("\nDone. You can tweak RANDOM_SEED, NOISE_STRENGTH, CENTRAL_FEATURE_SCALE,")
    print("USE_GAUSSIAN_BLUR, and BLUR_SIGMA at the top of the script for different map styles.")