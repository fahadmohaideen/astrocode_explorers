import pygame
import math
import random
from entities.bullet import Bullet
from core.constants import (
    WIDTH, HEIGHT, RED, GREEN, WHITE,
    ALIEN_MAX_HEALTH, BULLET_SPEED, DAMAGE_PER_HIT, ALIEN_TYPES
)

class Alien:
    def __init__(self, x, y, name):
        self.width = 60
        self.height = 60
        self.pos = pygame.Vector2(x + self.width / 2, y + self.height / 2)
        self.offset_pos = self.pos
        self.active = True
        self.name = name
        self.health = ALIEN_MAX_HEALTH
        self.prev_time = pygame.time.get_ticks() + random.randint(0, 500)
        self.bullets = []
        self.shoot_cooldown = 1000
        self.detection_range = 2500
        self.disappearing = False
        self.disappear_timer = 0
        self.disappear_duration = 30
        self.shielded = False
        self.shield_timer = pygame.time.get_ticks()
        self.shield_down_duration = 2000
        self.shield_up_duration = 5000

    def update_shield(self):
        current_time = pygame.time.get_ticks()
        if self.shielded and (current_time - self.shield_timer > self.shield_up_duration):
            self.shielded = False
            self.shield_timer = current_time
        elif not self.shielded and (current_time - self.shield_timer > self.shield_down_duration):
            self.shielded = True
            self.shield_timer = current_time

    def update_bullets(self, player, level_id, dt):
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue
            bullet.pos.x += bullet.dx * dt
            bullet.pos.y += bullet.dy * dt
            if not (-100 < bullet.pos.x < WIDTH + 100 and -100 < bullet.pos.y < HEIGHT + 100):
                bullet.active = False
                continue
            if not player.is_dying:
                distance = bullet.pos.distance_to(player.pos)
                collision_threshold = player.width / 2 + bullet.radius
                if distance < collision_threshold:
                    player.health -= DAMAGE_PER_HIT
                    bullet.active = False
        self.bullets = [b for b in self.bullets if b.active]

    def shoot_bullet(self, target_pos, color):
        if not self.active:
            return
        direction = (target_pos - self.pos).normalize()
        bullet = Bullet(self.pos.x, self.pos.y, direction.x * BULLET_SPEED, direction.y * BULLET_SPEED,
                        bullet_type=self.name, color=color)
        self.bullets.append(bullet)

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
        if image:
            alien_rect = image.get_rect(center=self.offset_pos)
            surface.blit(image, alien_rect)
        if self.shielded:
            shield_radius = self.width / 2 + 10
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 100, 255, 100), (shield_radius, shield_radius), shield_radius)
            surface.blit(shield_surface, (self.offset_pos.x - shield_radius, self.offset_pos.y - shield_radius))
        self.draw_health_bar(surface)
