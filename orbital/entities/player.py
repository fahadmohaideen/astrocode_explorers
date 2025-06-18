# Player class with movement and shooting
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
        self.angle = angle  # Angle in degrees (0 = up, 90 = right, etc.)
        self.width = width
        self.height = height
        self.bullets = []  # List of active Bullet objects
        self.max_bullets = 50
        self.bullet_pool = []  # List of inactive Bullet objects for recycling
        self.damage_dealt = False  # Flag to indicate if this player's bullet hit something
        self.health = PLAYER_MAX_HEALTH
        self.last_hit_bullet_shape = None  # Stores the shape of the last bullet that hit this player

    def draw_player(self, surface):
        """Draws the player (robot) on the given surface."""
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, CYAN, body_rect)

        # Gun (rotated based on angle)
        gun_length = self.height * 1.5
        gun_center = (body_rect.centerx, body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    def draw_health_bar(self, surface):
        """Draws the player's health bar."""
        bar_width = self.width * 2
        bar_height = 10
        bar_x = self.x + self.width // 2 - bar_width // 2
        bar_y = self.y - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / PLAYER_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def _init_bullet(self, bullet, x, y, angle, width, height):
        """Initializes properties of a bullet before it's fired."""
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
        # current_time = pygame.time.get_ticks()
        # print(current_time)
        # if current_time - self.last_shot_time < self.shot_cooldown:
        # return

        # self.last_shot_time = current_time

        # Reuse inactive bullets first
        for bullet in self.bullet_pool:
            if not bullet.active:
                self._init_bullet(bullet, self.x, self.y, self.angle, self.width, self.height)
                return

        # Create new bullet if pool is empty
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(shape=shape)
            self._init_bullet(bullet, self.x, self.y, self.angle, self.width, self.height)
            self.bullets.append(bullet)

    def update_bullets(self, target, level_id, dt):
        self.damage_dealt = False
        #target = self.target  # Cache target reference

        for bullet in self.bullets:
            if not bullet.active:
                continue

            # Update position
            bullet.x += bullet.dx * dt * BULLET_SPEED
            bullet.y += bullet.dy * dt * BULLET_SPEED
            #self.current_bullet = bullet

            # Boundary check
            if not (0 <= bullet.x < WIDTH and 0 <= bullet.y < HEIGHT):
                bullet.active = False
                continue

            # Fast AABB collision check
            if (target.x - BULLET_RADIUS <= bullet.x <= target.x + target.width + BULLET_RADIUS and
                    target.y - BULLET_RADIUS <= bullet.y <= target.y + target.height + BULLET_RADIUS):
                bullet.active = False
                self.damage_dealt = True

        # Remove inactive bullets (do this less frequently)
        if random.random() < 0.1:  # Only clean up 10% of frames
            self.bullets = [b for b in self.bullets if b.active]
            self.bullet_pool = [b for b in self.bullets if not b.active]
        self.bullets = [b for b in self.bullets if b.active]

        if self.damage_dealt:
            if level_id == 1 or level_id == 2:
                target.health = max(0, target.health - DAMAGE_PER_HIT)

