import pygame
import sys

# Initialize pygame mixer and pygame for input
pygame.mixer.init()
pygame.init()

# Load the sample filenames from an external text file
def load_samples_from_file(file_path):
    with open(file_path, 'r') as f:
        samples = [line.strip() for line in f.readlines()]
    return samples

# Assign keys in QWERTY order
qwerty_keys = [
    pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t,
    pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p,
    pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g,
    pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l,
    pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b, pygame.K_n, pygame.K_m
]

# Load all samples from a text file
all_samples = load_samples_from_file('samples.txt')

# Determine the number of batches and samples per batch
samples_per_batch = 26
total_batches = (len(all_samples) + samples_per_batch - 1) // samples_per_batch  # ceiling division

# Set up a screen (even though we won't be using it)
screen = pygame.display.set_mode((800, 300))
pygame.display.set_caption('Sample Player')

# Set up the font
pygame.font.init()
font = pygame.font.SysFont(None, 48)

# Track the current batch index
current_batch = 0

# This dictionary will hold the currently playing sounds by key
current_sounds = {}

# Variable to store the currently displayed filename
current_filename = ""

# Function to display the current filename on the screen
def display_filename(filename):
    screen.fill((0, 0, 0))  # Clear the screen with black background
    text_surface = font.render(filename, True, (255, 255, 255))  # White text
    screen.blit(text_surface, (20, 120))  # Display in the center area
    pygame.display.update()  # Update the screen

# Function to play a sound based on the key
def play_sound(key):
    global current_sounds, current_filename
    
    # Calculate the index in the current batch for this key
    key_index = qwerty_keys.index(key) if key in qwerty_keys else None
    
    if key_index is not None:
        sample_index = current_batch * samples_per_batch + key_index
        if sample_index < len(all_samples):
            sound_file = all_samples[sample_index]
            new_sound = pygame.mixer.Sound(sound_file)
            
            # Stop the currently playing sound for the key, if any
            if key in current_sounds:
                current_sounds[key].stop()

            # Play the new sound and store it
            current_sounds[key] = new_sound
            new_sound.play()
            
            # Update the current filename and display it
            current_filename = sound_file
            display_filename(current_filename)

# Switch to a specific batch based on a number (1 to 9 keys)
def select_batch_by_number(number):
    global current_batch
    if 0 <= number < 9 and number < total_batches:  # Only allow numbers in range and available batches
        current_batch = number

def main():
    global current_batch
    
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle key press events
            if event.type == pygame.KEYDOWN:
                # If it's a qwerty key, play the associated sound
                if event.key in qwerty_keys:
                    play_sound(event.key)
                
                # Left arrow key to move to the previous batch
                elif event.key == pygame.K_LEFT:
                    current_batch = (current_batch - 1) % total_batches
                
                # Right arrow key to move to the next batch
                elif event.key == pygame.K_RIGHT:
                    current_batch = (current_batch + 1) % total_batches

                # Number keys (1 to 9) to select specific batches
                elif event.key == pygame.K_1:
                    select_batch_by_number(0)  # Batch 0
                elif event.key == pygame.K_2:
                    select_batch_by_number(1)  # Batch 1
                elif event.key == pygame.K_3:
                    select_batch_by_number(2)  # Batch 2
                elif event.key == pygame.K_4:
                    select_batch_by_number(3)  # Batch 3
                elif event.key == pygame.K_5:
                    select_batch_by_number(4)  # Batch 4
                elif event.key == pygame.K_6:
                    select_batch_by_number(5)  # Batch 5
                elif event.key == pygame.K_7:
                    select_batch_by_number(6)  # Batch 6
                elif event.key == pygame.K_8:
                    select_batch_by_number(7)  # Batch 7
                elif event.key == pygame.K_9:
                    select_batch_by_number(8)  # Batch 8

                # Print the current batch (optional for debugging)
                print(f"Current batch: {current_batch + 1}/{total_batches}")

if __name__ == "__main__":
    main()


