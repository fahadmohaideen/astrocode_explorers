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
        self.color = color
        self.image = None  # Will hold the loaded image

        # Load appropriate image based on bullet type
        # Change all image paths from "assets/..." to "levels/assets/..."
        try:
            if bullet_type == "Alien Type A":
                img_path = os.path.join("levels", "assets", "bullet_red.png")
                self.image = pygame.image.load(img_path).convert_alpha()
            elif bullet_type == "Alien Type B":
                img_path = os.path.join("levels", "assets", "bullet_green.png")
                self.image = pygame.image.load(img_path).convert_alpha()
            elif bullet_type == "Alien Type C":
                img_path = os.path.join("levels", "assets", "bullet_blue.png")
                self.image = pygame.image.load(img_path).convert_alpha()

            # Scale if image was loaded
            if self.image:
                self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
        except Exception as e:
            print(f"Error loading bullet image: {e}")
            self.image = None

    def draw(self, surface, camera_offset):
        if not self.active or not self.image:
            return

        adjusted_pos = self.pos - camera_offset
        surface.blit(self.image, (adjusted_pos.x - self.radius, adjusted_pos.y - self.radius))

    def _draw_circle(self, surface, color, camera_offset):
        """Draws a circular bullet."""
        adjusted_pos = self.pos - camera_offset
        bullet_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surface, color, (self.radius, self.radius), self.radius)
        surface.blit(bullet_surface, (adjusted_pos.x - self.radius, adjusted_pos.y - self.radius))

    def reactivate(self, x, y, direction):
        """Reuse an existing bullet"""
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.dx = direction.x * BULLET_SPEED
        self.dy = direction.y * BULLET_SPEED
        self.active = True

