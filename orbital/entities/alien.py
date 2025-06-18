
import pygame
import math
import random
from entities.player import Player

from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT
)

class Alien(Player):
    def __init__(self):
        super().__init__()
        self.x = 60
        self.y = 160
        self.angle = 90
        self.width = 60
        self.height = 60
        self.body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.shape_options = ["circle", "square", "triangle"]
        self.prev_time = pygame.time.get_ticks()
        self.health = TARGET_MAX_HEALTH

    def draw_health_bar(self, surface):
        bar_width = self.width
        bar_height = 10
        bar_x = self.x
        bar_y = self.y - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def shoot_alien_bullets(self):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.prev_time >= 1500:
            self.shoot_bullet(self.shape_options[random.randint(0, 2)])
            self.prev_time = curr_time