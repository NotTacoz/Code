
import csv
import random

MAP_DIMENSION = 128
OUTPUT_FILENAME = "map.csv"

def generate_map_data(dimension: int) -> list[list[float]]:
    """Generates a 2D list of random float values for the map."""
    map_data = []
    for _ in range(dimension):
        row = [round(random.uniform(0.0, 1.0), 3) for _ in range(dimension)]
        map_data.append(row)
    return map_data

def save_map_to_csv(map_data: list[list[float]], filename: str) -> None:
    """Saves the map data to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in map_data:
                writer.writerow(row)
        print(f"Successfully generated and saved {filename} ({len(map_data)}x{len(map_data[0])})")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")

if __name__ == "__main__":
    print(f"Generating a {MAP_DIMENSION}x{MAP_DIMENSION} map, please wait...")
    terrain_data = generate_map_data(MAP_DIMENSION)
    save_map_to_csv(terrain_data, OUTPUT_FILENAME)
