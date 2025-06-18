
import pygame
import math
import random
from entities.bullet import Bullet
from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT
)


class Player:
    def __init__(self, x=0, y=0, width=0, height=0, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.width = width
        self.height = height
        self.bullets = []
        self.max_bullets = 50
        self.bullet_pool = []
        self.damage_dealt = False
        self.health = PLAYER_MAX_HEALTH
        self.last_hit_bullet_shape = None

    def draw_player(self, surface):
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, CYAN, body_rect)

        gun_length = self.height * 1.5
        gun_center = (body_rect.centerx, body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    def draw_health_bar(self, surface):
        bar_width = self.width * 2
        bar_height = 10
        bar_x = self.x + self.width // 2 - bar_width // 2
        bar_y = self.y - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / PLAYER_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def _init_bullet(self, bullet, x, y, angle, width, height):
        angle_rad = math.radians(angle)
        center_x = x + width // 2
        center_y = y + height // 2
        gun_length = height * 1.5

        bullet.x = center_x + gun_length * math.sin(angle_rad)
        bullet.y = center_y - gun_length * math.cos(angle_rad)
        bullet.dx = math.sin(angle_rad)
        bullet.dy = -math.cos(angle_rad)
        bullet.radius = BULLET_RADIUS
        bullet.active = True

    def shoot_bullet(self, shape):
        for bullet in self.bullet_pool:
            if not bullet.active:
                self._init_bullet(bullet, self.x, self.y, self.angle, self.width, self.height)
                return
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(shape=shape)
            self._init_bullet(bullet, self.x, self.y, self.angle, self.width, self.height)
            self.bullets.append(bullet)

    def update_bullets(self, target, level_id, dt):
        self.damage_dealt = False
        for bullet in self.bullets:
            if not bullet.active:
                continue
            bullet.x += bullet.dx * dt * BULLET_SPEED
            bullet.y += bullet.dy * dt * BULLET_SPEED
            
            if not (0 <= bullet.x < WIDTH and 0 <= bullet.y < HEIGHT):
                bullet.active = False
                continue
            
            if (target.x - BULLET_RADIUS <= bullet.x <= target.x + target.width + BULLET_RADIUS and
                    target.y - BULLET_RADIUS <= bullet.y <= target.y + target.height + BULLET_RADIUS):
                bullet.active = False
                self.damage_dealt = True

        if random.random() < 0.1:
            self.bullets = [b for b in self.bullets if b.active]
            self.bullet_pool = [b for b in self.bullets if not b.active]
        self.bullets = [b for b in self.bullets if b.active]

        if self.damage_dealt:
            if level_id == 1 or level_id == 2:
                target.health = max(0, target.health - DAMAGE_PER_HIT)

