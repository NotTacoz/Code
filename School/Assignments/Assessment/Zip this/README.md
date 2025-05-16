## Synopsis
Practical Assignment for Fundamentals of Programming COMP1005. Untitled Bee Simulator is my attempt at generating a 2d top down simulator of creatures and interaction with the external world. The engine is based of pygame, which offered me the opportunity to learn an exciting new library.

## Contents
-   `main.py`: The main Python script for running the program.
-   `params.csv`: CSV file containing parameters for the program.
-   `map_oasis.csv`: CSV file representing an oasis map.
-   `test_map.csv`: CSV file representing a test map.
-   `random_noise_map.csv`: CSV file representing a map generated with random noise.
-   `requirements.txt`: A text file listing the Python package dependencies.
-   `flower.png`: Image file for a flower asset.
-   `bee.png`: Image file for a bee asset.
-   `README.md`: This readme file.

## Dependencies
The program requires the following Python libraries:
-   matplotlib==3.10.3
-   noise==1.2.2
-   numpy==2.2.5
-   pygame==2.6.1

To install the dependencies, run:
```bash
pip install -r requirements.txt
```

## How to Run
### Basic Setup
To run the program, execute the `main.py` script from your terminal:
```bash
$ python main.py
```

### Interactive Mode (prompts for parameters):
```bash
$ python main.py -i
```

With a Specific Seed:
```bash
$ python main.py -s 12345
```

Batch Mode (using predefined map and parameter files):
```bash
$ python main.py -b -f <map_filename.csv> -p <parameter_filename.csv>
```

Example:
```bash
$ python main.py -b -f scenario_map.csv -p scenario_params.csv -s <seed>
```


*Note: For batch mode, you need to provide CSV files for the map and parameters as described in the main project report.*

### Key Controls (During Simulation)
Pan Camera: Move mouse to screen edges.
Zoom In: `=` or `+` key.
Zoom Out: `-` key.
Select Entity: Left-click on a bee or hive to view its details.

Ensure that all CSV map files and image assets are in the same directory as `main.py`, or update the paths within the script accordingly.

## Version information
May 12, 2025 - Final version of "Untitled Bee Simulation"