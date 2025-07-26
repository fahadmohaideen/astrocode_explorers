import os
import pygame
import math
import random
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(os.path.dirname(script_dir), "levels", "assets")

from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT
)


class Bullet:
    def __init__(self, x=0, y=0, dx=0, dy=0, bullet_type="", color=None, radius=12):
        self.pos = pygame.Vector2(x, y)
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.active = True
        self.bullet_type = bullet_type
        self.color = color or RED
        self.image = None
        self._load_bullet_image()
        if self.image:
            angle = math.degrees(math.atan2(-self.dy, self.dx))
            self.image = pygame.transform.rotate(self.image, angle)
            self.radius = max(self.image.get_width(), self.image.get_height()) // 2
        if self.image:
            self.rendered_image = self._create_optimized_surface()

    def _load_bullet_image(self):
        if not self.bullet_type:
            return

        bullet_sizes = {
            "Alien Type A": 50,
            "Alien Type B": 50,
            "Alien Type C": 50,
        }

        bullet_images = {
            "Alien Type A": "bullet_red.png",
            "Alien Type B": "bullet_green.png",
            "Alien Type C": "bullet_blue.png",
        }

        if self.bullet_type in bullet_images:
            try:
                img_path = os.path.join(ASSETS_PATH, bullet_images[self.bullet_type])
                if os.path.exists(img_path):
                    original_img = pygame.image.load(img_path).convert_alpha()

                    target_size = bullet_sizes[self.bullet_type]
                    self.image = pygame.transform.scale(
                        original_img,
                        (target_size, target_size)
                    )

                    self.radius = target_size // 2
            except Exception as e:
                print(f"Error loading bullet image: {e}")

    def _create_optimized_surface(self):
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        surf.blit(self.image, (0, 0))
        return surf

    def draw(self, surface, camera_offset):
        if not self.active:
            return

        pos = self.pos - camera_offset
        if hasattr(self, 'rendered_image'):
            surface.blit(self.rendered_image, (pos.x - self.radius, pos.y - self.radius))
        else:
            pygame.draw.circle(surface, self.color, (int(pos.x), int(pos.y)), self.radius)

    def reactivate(self, x, y, direction):
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.dx = direction.x * BULLET_SPEED
        self.dy = direction.y * BULLET_SPEED
        self.active = True
