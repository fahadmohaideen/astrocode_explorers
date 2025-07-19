
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
        self.angle = angle
        self.speed = speed
        #self.body_rect = pygame.Rect(self.offset_pos.x, self.offset_pos.y, self.width, self.height)
        self.bullets = []
        self.max_bullets = 50
        self.bullet_pool = []
        self.damage_dealt = False
        self.health = PLAYER_MAX_HEALTH
        self.last_hit_bullet_shape = None

    def draw_player(self, surface, img):
        self.body_rect = pygame.Rect(self.offset_pos.x-self.width/2, self.offset_pos.y-self.height/2, self.width, self.height)
        surface.blit(img, (self.offset_pos.x-self.width/2, self.offset_pos.y-self.height/2))

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
        bar_width = self.width
        bar_height = 10
        bar_x = self.offset_pos.x - self.width/2
        bar_y = self.offset_pos.y - self.height/2 - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def _init_bullet(self, bullet, x, y, angle, width, height):
        angle_rad = math.radians(angle)
        gun_length = height * 1.5

        bullet.pos.x = x + gun_length * math.sin(angle_rad)
        bullet.pos.y = y - gun_length * math.cos(angle_rad)
        bullet.dx = math.sin(angle_rad) * BULLET_SPEED
        bullet.dy = -math.cos(angle_rad) * BULLET_SPEED
        bullet.active = True

    def shoot_bullet(self, bullet_type, alien_pos, color):
        direction = (alien_pos - self.pos).normalize()
        self.angle = pygame.Vector2(0, -1).angle_to(direction)

        bullet = Bullet(
            x=self.pos.x,
            y=self.pos.y,
            dx=direction.x * BULLET_SPEED,
            dy=direction.y * BULLET_SPEED,
            bullet_type=bullet_type,
            color=color
        )
        self.bullets.append(bullet)
        return bullet

    def update_bullets(self, targets, level_id, dt):
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue

            bullet.pos.x += bullet.dx * dt
            bullet.pos.y += bullet.dy * dt

            if not (0 <= bullet.pos.x <= WIDTH and 0 <= bullet.pos.y <= HEIGHT):
                bullet.active = False
                continue

            for target in targets:
                if target.active and bullet.pos.distance_to(target.pos) < target.width / 2 + bullet.radius:
                    bullet.active = False
                    target.health -= DAMAGE_PER_HIT
                    break



