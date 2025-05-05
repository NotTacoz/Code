import os
import random
import time
import pygame
from datetime import datetime

def play_random_mp3(folder_path):
    """
    Plays a random MP3 file from the specified folder.
    
    Args:
        folder_path (str): Path to folder containing MP3 files
    
    Returns:
        str: Name of the file that was played or None if no files were found
    """
    # Get all MP3 files in the folder
    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
    
    if not mp3_files:
        print(f"No MP3 files found in {folder_path}")
        return None
    
    # Select a random MP3 file
    selected_file = random.choice(mp3_files)
    file_path = os.path.join(folder_path, selected_file)
    
    # Play the selected MP3 file
    print(f"{datetime.now().strftime('%H:%M:%S')} - Playing: {selected_file} (volume: 20%)")
    
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.2)  # Set volume to 20% of maximum
    pygame.mixer.music.play()
    
    # Wait for the file to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    return selected_file

def main():
    """
    Main function that plays random MP3 files at random intervals.
    """
    # Set the path to the sounds folder
    sounds_folder = "sounds"
    
    # Ensure the sounds folder exists
    if not os.path.exists(sounds_folder):
        print(f"Folder '{sounds_folder}' does not exist. Creating it...")
        os.makedirs(sounds_folder)
        print(f"Please add MP3 files to the '{sounds_folder}' folder and run the script again.")
        return
    
    # Set the minimum and maximum intervals between plays (in seconds)
    min_interval = 10  # Minimum 10 seconds between plays
    max_interval = 60  # Maximum 60 seconds between plays
    
    print(f"Starting random MP3 player. Monitoring folder: {sounds_folder}")
    print(f"Will play files at random intervals between {min_interval} and {max_interval} seconds.")
    print("Press Ctrl+C to stop the player.")
    
    try:
        while True:
            # Play a random MP3 file
            played_file = play_random_mp3(sounds_folder)
            
            if played_file:
                # Wait for a random interval before playing the next file
                wait_time = random.randint(min_interval, max_interval)
                print(f"Waiting {wait_time} seconds before playing the next file...")
                time.sleep(wait_time)
            else:
                # If no MP3 files were found, wait a bit and check again
                print("Waiting 30 seconds before checking for MP3 files again...")
                time.sleep(30)
    
    except KeyboardInterrupt:
        print("\nRandom MP3 player stopped.")
        pygame.mixer.quit()

if __name__ == "__main__":
    main()
