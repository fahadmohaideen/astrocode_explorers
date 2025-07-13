# Bullet class and types
import pygame
import math
import random

from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT
)


class Bullet:
    __slots__ = ('x', 'y', 'dx', 'dy', 'radius', 'active', 'bullet_type', 'color', 'pos')

    def __init__(self, x=0, y=0, dx=0, dy=0, radius=0, active=False, bullet_type="", color=None):
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x, y)
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.active = active
        self.bullet_type = bullet_type
        self.color = color

    def draw(self, surface, camera_offset):  # Pass surface to draw
        """Draw the bullet based on its shape type."""
        self._draw_circle(surface, self.color, camera_offset)
        """elif self.shape == "square":
            self._draw_square(surface)
        elif self.shape == "triangle":
            self._draw_triangle(surface)"""

    def _draw_circle(self, surface, color, camera_offset):
        """Draws a circular bullet."""
        adjusted_pos = self.pos - camera_offset
        bullet_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surface, color, (self.radius, self.radius), self.radius)
        surface.blit(bullet_surface, (adjusted_pos.x - self.radius, adjusted_pos.y - self.radius))

    """def _draw_square(self, surface):
        size = self.radius * 2
        bullet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, BLUE, (0, 0, size, size), border_radius=3)
        surface.blit(bullet_surface, (self.x - self.radius, self.y - self.radius))

    def _draw_triangle(self, surface):
        height = self.radius * 2
        width = height * 0.866  # Equilateral triangle ratio

        bullet_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        points = [
            (width // 2, 0),
            (0, height),
            (width, height)
        ]
        pygame.draw.polygon(bullet_surface, GREEN, points)
        surface.blit(bullet_surface, (self.x - width // 2, self.y - height // 2))"""