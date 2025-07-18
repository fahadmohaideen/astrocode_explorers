# Bullet class and types
import pygame
import math
import random
import os
ASSETS_PATH = os.path.join("levels", "assets")

from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT
)


class Bullet:
    __slots__ = ('x', 'y', 'dx', 'dy', 'radius', 'active', 'bullet_type', 'color', 'pos', 'image')

    def __init__(self, x=0, y=0, dx=0, dy=0, bullet_type="", color=None, radius=BULLET_RADIUS):
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.active = True
        self.bullet_type = bullet_type
        self.color = color or RED
        self.image = None

        # Map bullet types to image files
        type_to_image = {
            "Alien Type A": "bullet_red.png",
            "Alien Type B": "bullet_green.png",
            "Alien Type C": "bullet_blue.png"
        }

        if bullet_type in type_to_image:
            try:
                img_path = os.path.join("levels", "assets", type_to_image[bullet_type])
                if os.path.exists(img_path):
                    self.image = pygame.image.load(img_path).convert_alpha()
                    self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
                    print(f"Successfully loaded image for {bullet_type}")
                else:
                    print(f"Image not found at: {os.path.abspath(img_path)}")
            except Exception as e:
                print(f"Error loading {bullet_type} image: {e}")

    def draw(self, surface, camera_offset):
        if not self.active:
            return

        adjusted_pos = self.pos - camera_offset

        # Draw image if available, otherwise draw colored circle
        if self.image:
            surface.blit(self.image, (adjusted_pos.x - self.radius, adjusted_pos.y - self.radius))
        else:
            pygame.draw.circle(surface, self.color,
                               (int(adjusted_pos.x), int(adjusted_pos.y)),
                               self.radius)

    def reactivate(self, x, y, direction):
        """Reuse an existing bullet"""
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.dx = direction.x * BULLET_SPEED
        self.dy = direction.y * BULLET_SPEED
        self.active = True
