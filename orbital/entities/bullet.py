# Bullet class and types
import pygame
import math
import random

from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT
)


class Bullet:
    __slots__ = ('x', 'y', 'dx', 'dy', 'radius', 'active', 'shape')

    def __init__(self, x=None, y=None, dx=None, dy=None, radius=None, active=False, shape="circle"):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.active = active
        self.shape = shape  # "circle", "square", "triangle"

    def draw(self, surface):  # Pass surface to draw
        """Draw the bullet based on its shape type."""
        if self.shape == "circle":
            self._draw_circle(surface)
        elif self.shape == "square":
            self._draw_square(surface)
        elif self.shape == "triangle":
            self._draw_triangle(surface)

    def _draw_circle(self, surface):
        """Draws a circular bullet."""
        bullet_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surface, ORANGE, (self.radius, self.radius), self.radius)
        surface.blit(bullet_surface, (self.x - self.radius, self.y - self.radius))

    def _draw_square(self, surface):
        """Draws a square bullet."""
        size = self.radius * 2
        bullet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, BLUE, (0, 0, size, size), border_radius=3)
        surface.blit(bullet_surface, (self.x - self.radius, self.y - self.radius))

    def _draw_triangle(self, surface):
        """Draws a triangular bullet."""
        height = self.radius * 2
        width = height * 0.866  # Equilateral triangle ratio

        bullet_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        points = [
            (width // 2, 0),
            (0, height),
            (width, height)
        ]
        pygame.draw.polygon(bullet_surface, GREEN, points)
        surface.blit(bullet_surface, (self.x - width // 2, self.y - height // 2))