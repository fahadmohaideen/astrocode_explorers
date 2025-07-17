import pygame
import math
import random
from entities.player import Player, Bullet
from core.constants import ALIEN_MAX_HEALTH, TARGET_MAX_HEALTH

from core.constants import (


    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH,
    TARGET_MAX_HEALTH, DAMAGE_PER_HIT, ALIEN_TYPES,
    ALIEN_MAX_HEALTH
)


class Alien(Player):
    def __init__(self, x, y, name):
        super().__init__()
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.pos = pygame.Vector2(self.x + self.width / 2, self.y + self.height / 2)
        self.offset_pos = self.pos
        self.angle = 90
        self.active = True
        self.health = ALIEN_MAX_HEALTH
        self.name = name
        self.image = None
        self.shape_options = ["circle", "square", "triangle"]
        self.prev_time = 0
        self.bullets = []
        self.bullet_pool = []
        self.shoot_cooldown = 1000
        self.detection_range = 500

    def update(self, dt, player=None):
        for bullet in self.bullets:
            if bullet.active:
                bullet.update(dt)
            else:
                self.bullet_pool.append(bullet)

        self.bullets = [b for b in self.bullets if b.active]

        if self.health <= 0:
            self.active = False

    def shoot_bullet(self, target_pos, color):
        if not self.active:
            return None

        direction = (target_pos - self.pos).normalize()

        if self.bullet_pool:
            bullet = self.bullet_pool.pop()
            bullet.reactivate(self.pos.x, self.pos.y, direction)
        else:
            bullet = Bullet(
                self.pos.x, self.pos.y,
                direction.x * BULLET_SPEED,
                direction.y * BULLET_SPEED,
                bullet_type=self.name,
                color=color
            )

        self.bullets.append(bullet)
        return bullet

    def shoot_at_player(self, player, dt):
        if not self.active or not player:
            return

        curr_time = pygame.time.get_ticks()
        distance_to_player = (player.pos - self.pos).length()

        if (curr_time - self.prev_time >= self.shoot_cooldown and
                distance_to_player < self.detection_range):
            self.shoot_bullet(player.pos, ALIEN_TYPES.get(self.name, RED))
            self.prev_time = curr_time

    def draw_health_bar(self, surface):
        if not self.active:
            return

        bar_width = self.width
        bar_height = 8
        bar_x = self.offset_pos.x - self.width / 2
        bar_y = self.offset_pos.y - self.height / 2 - 15

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))

        health_width = (self.health / ALIEN_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def draw(self, surface, image=None):
        if not self.active:
            return

        draw_image = image if image is not None else self.image

        if draw_image:
            alien_rect = draw_image.get_rect(center=self.offset_pos)
            surface.blit(draw_image, alien_rect)
        else:
            pygame.draw.rect(
                surface,
                ALIEN_TYPES.get(self.name, RED),
                (self.offset_pos.x - self.width / 2,
                 self.offset_pos.y - self.height / 2,
                 self.width, self.height)
            )

        self.draw_health_bar(surface)
