import pygame
import random
import math

from core.constants import WIDTH, HEIGHT, WHITE


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
    for pos, speed, size in stars:
        alpha = int(100 + 155 * (1 - speed))
        color = (alpha, alpha, alpha)
        pygame.draw.circle(surface, color, (int(pos.x), int(pos.y)), size)

def update_starfield(dt):
    global twinkle_timer
    for i, (pos, speed, size) in enumerate(stars):
        pos.x += speed * 10 * dt
        if pos.x > WIDTH:
            pos.x = 0
            pos.y = random.randint(0, HEIGHT)
        stars[i] = (pos, speed, size)

    twinkle_timer += dt
    if twinkle_timer >= twinkle_delay:
        twinkle_timer = 0
        for _ in range(5):
            idx = random.randint(0, len(stars) - 1)
            stars[idx] = (stars[idx][0], stars[idx][1], random.randint(1, 3))
