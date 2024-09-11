import pygame
import sys

# Initialize pygame mixer for sound playback
pygame.mixer.init()

# Initialize pygame for keyboard input
pygame.init()

# Load your sound samples here (make sure the files are in the same directory or provide the full path)
# The tuple structure is now (filename, interruptible, group), where 'group' is used to categorize sounds.
sound_files = {
    pygame.K_a: ('sample1.wav', True, 'group1'),   # Interruptible sound in group1
    pygame.K_s: ('sample2.wav', False, 'group2'),  # Non-interruptible sound in group2
    pygame.K_d: ('sample3.wav', True, 'group1'),   # Interruptible sound in group1
    pygame.K_f: ('sample4.wav', True, 'group3'),   # Interruptible sound in group3
    pygame.K_g: ('sample5.wav', False, 'group2'),  # Non-interruptible sound in group2
}

# Set up a screen (even though we won't be using it)
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Sample Player')

# This dictionary will hold the currently playing sounds, categorized by group
current_sounds = {}

def play_sound(key):
    global current_sounds
    
    if key in sound_files:
        sound_file, interruptible, group = sound_files[key]
        
        # Load the new sound
        new_sound = pygame.mixer.Sound(sound_file)
        
        # Check if the sound is interruptible
        if interruptible:
            # Stop any currently playing sound in the same group
            if group in current_sounds and current_sounds[group] is not None:
                current_sounds[group].stop()  # Stop the sound in the same group
            # Play the new sound and store it in the current_sounds for the group
            current_sounds[group] = new_sound
            new_sound.play()
        else:
            # If the sound is non-interruptible, it just plays without stopping anything
            new_sound.play()

def main():
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # If a key is pressed, play the associated sound
                play_sound(event.key)

if __name__ == "__main__":
    main()

