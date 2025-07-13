# Alien logic and bullets
import pygame
import math
import random
from entities.player import Player

from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT, ALIEN_TYPES
)

class Alien(Player):
    def __init__(self, x, y, name):
        super().__init__()
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.pos = pygame.Vector2(self.x + self.width/2, self.y + self.height/2)
        self.offset_pos = self.pos
        self.angle = 90
        #self.body_rect = pygame.Rect(self.offset_pos.x, self.offset_pos.y, self.width, self.height)
        self.shape_options = ["circle", "square", "triangle"]
        self.prev_time = 0  # Initialize with current ticks for consistent timing
        self.health = TARGET_MAX_HEALTH  # Alien uses TARGET_MAX_HEALTH
        self.name = name
    """def draw_health_bar(self, surface):
        
        bar_width = self.width
        bar_height = 10
        bar_x = self.x
        bar_y = self.y - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)"""

    def shoot_alien_bullets(self, player, dt):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.prev_time >= 500:  # Original cooldown
            self.shoot_bullet(None, player.pos, (255, 100, 255))
            self.prev_time = curr_time