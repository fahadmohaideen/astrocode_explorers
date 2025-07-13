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
    def __init__(self, x=0, y=0, width=0, height=0, angle=0, speed=0):
        self.body_rect = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.pos = pygame.Vector2(self.x + self.width/2, self.y + self.height/2)
        self.offset_pos = self.pos
        self.angle = angle  # Angle in degrees (0 = up, 90 = right, etc.)
        self.speed = speed
        #self.body_rect = pygame.Rect(self.offset_pos.x, self.offset_pos.y, self.width, self.height)
        self.bullets = []  # List of active Bullet objects
        self.max_bullets = 50
        self.bullet_pool = []  # List of inactive Bullet objects for recycling
        self.damage_dealt = False  # Flag to indicate if this player's bullet hit something
        self.health = PLAYER_MAX_HEALTH
        self.last_hit_bullet_shape = None  # Stores the shape of the last bullet that hit this player

    def draw_player(self, surface, img):
        """Draws the player (robot) on the given surface."""
        #body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.body_rect = pygame.Rect(self.offset_pos.x-self.width/2, self.offset_pos.y-self.height/2, self.width, self.height)
        #pygame.draw.rect(surface, CYAN, self.body_rect)
        surface.blit(img, (self.offset_pos.x-self.width/2, self.offset_pos.y-self.height/2))

        # Gun (rotated based on angle)
        gun_length = self.height * 1.5
        gun_center = (self.body_rect.centerx, self.body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    """def draw_health_bar(self, surface):
        
        bar_width = self.width * 2
        bar_height = 10
        bar_x = self.offset_pos.x + self.width // 2 - bar_width // 2
        bar_y = self.offset_pos.y - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / PLAYER_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)"""

    def draw_health_bar(self, surface):
        """Draws the alien's health bar."""
        bar_width = self.width
        bar_height = 10
        bar_x = self.offset_pos.x - self.width/2
        bar_y = self.offset_pos.y - self.height/2 - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def _init_bullet(self, bullet, x, y, angle, width, height):
        """Initializes properties of a bullet before it's fired."""
        angle_rad = math.radians(angle)
        center_x = x
        center_y = y
        gun_length = height * 1.5

        bullet.pos.x = center_x + gun_length * math.sin(angle_rad)
        bullet.pos.y = center_y - gun_length * math.cos(angle_rad)
        bullet.dx = math.sin(angle_rad)
        bullet.dy = -math.cos(angle_rad)
        bullet.radius = BULLET_RADIUS
        bullet.active = True

    def shoot_bullet(self, bullet_type, alien_pos, color):
        bullet_vec = self.pos - alien_pos
        vertical_vec = pygame.Vector2(0, 1)
        self.angle = vertical_vec.angle_to(bullet_vec)

        # Reuse inactive bullets first
        for bullet in self.bullet_pool:
            if not bullet.active:
                self._init_bullet(bullet, self.pos.x, self.pos.y, self.angle, self.width, self.height)
                return

        # Create new bullet if pool is empty
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(bullet_type=bullet_type, color=color)
            self._init_bullet(bullet, self.pos.x, self.pos.y, self.angle, self.width, self.height)
            self.bullets.append(bullet)

    def update_bullets(self, target, level_id, dt):
        self.damage_dealt = False
        #target = self.target  # Cache target reference
        prev_bullet = None

        for bullet in self.bullets:
            if not bullet.active:
                continue

            # Update position
            if not prev_bullet:
                bullet.pos.x += bullet.dx * dt * BULLET_SPEED
                bullet.pos.y += bullet.dy * dt * BULLET_SPEED
            else:
                if prev_bullet.pos.distance_to(bullet.pos) > 40:
                    bullet.pos.x += bullet.dx * dt * BULLET_SPEED
                    bullet.pos.y += bullet.dy * dt * BULLET_SPEED
            #self.current_bullet = bullet

            # Boundary check
            """if not (0 <= bullet.x < WIDTH and 0 <= bullet.y < HEIGHT):
                bullet.active = False
                continue"""

            # Fast AABB collision check
            if (target.pos.x - BULLET_RADIUS - target.width/2 <= bullet.pos.x <= target.pos.x + target.width/2 + BULLET_RADIUS and
                    target.pos.y - BULLET_RADIUS - target.height/2 <= bullet.pos.y <= target.pos.y + target.height/2 + BULLET_RADIUS):
                bullet.active = False
                print("damage")
                self.damage_dealt = True

            prev_bullet = bullet

        # Remove inactive bullets (do this less frequently)
        if random.random() < 0.1:  # Only clean up 10% of frames
            self.bullets = [b for b in self.bullets if b.active]
            self.bullet_pool = [b for b in self.bullets if not b.active]
        self.bullets = [b for b in self.bullets if b.active]

        if self.damage_dealt:
            target.health = max(0, target.health - DAMAGE_PER_HIT)

