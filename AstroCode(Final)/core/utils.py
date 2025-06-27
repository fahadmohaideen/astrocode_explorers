# Utility functions like collision checks

import pygame
import random
import math

from core.constants import WIDTH, HEIGHT, WHITE # Import necessary constants

# Starfield background variables (global to this module)
stars = []
for _ in range(200):
    x = pygame.math.Vector2(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )
    speed = random.uniform(0.1, 0.5)
    size = random.randint(1, 3)
    stars.append((x, speed, size))

twinkle_timer = 0
twinkle_delay = 0.1

def draw_starfield(surface):
    """Draws the starfield background on the given surface."""
    for pos, speed, size in stars:
        # Simple alpha effect based on speed (can be adjusted)
        alpha = int(100 + 155 * (1 - speed))
        color = (alpha, alpha, alpha) # Grayscale for stars
        pygame.draw.circle(surface, color, (int(pos.x), int(pos.y)), size)

def update_starfield(dt):
    """Updates the positions and twinkling of stars."""
    global twinkle_timer # Access global twinkle_timer
    for i, (pos, speed, size) in enumerate(stars):
        pos.x += speed * 10 * dt # Move stars horizontally
        if pos.x > WIDTH: # Reset star position if it goes off-screen
            pos.x = 0
            pos.y = random.randint(0, HEIGHT)
        stars[i] = (pos, speed, size) # Update tuple in list

    # Twinkling effect
    twinkle_timer += dt
    if twinkle_timer >= twinkle_delay:
        twinkle_timer = 0
        # Randomly change size of a few stars to simulate twinkling
        for _ in range(5): # Affect 5 random stars each twinkle cycle
            idx = random.randint(0, len(stars) - 1)
            stars[idx] = (stars[idx][0], stars[idx][1], random.randint(1, 3))