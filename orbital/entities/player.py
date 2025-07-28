
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
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.pos = pygame.Vector2(self.x + self.width/2, self.y + self.height/2)
        self.offset_pos = self.pos
        self.angle = angle 
        self.speed = speed
        self.body_rect = pygame.Rect(self.offset_pos.x - self.width / 2, self.offset_pos.y - self.height / 2,
                                     self.width, self.height)
        #self.body_rect = pygame.Rect(self.offset_pos.x, self.offset_pos.y, self.width, self.height)
        self.bullets = []
        self.max_bullets = 50
        self.bullet_pool = []
        self.damage_dealt = False
        self.health = PLAYER_MAX_HEALTH
        self.last_hit_bullet_shape = None
        self.bullet_index = 0
        self.bullet_vec = pygame.Vector2(0, 1)

    def draw_player(self, surface, img):
        #body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.body_rect = pygame.Rect(self.offset_pos.x-self.width/2, self.offset_pos.y-self.height/2, self.width, self.height)
        #pygame.draw.rect(surface, CYAN, self.body_rect)
        surface.blit(img, (self.offset_pos.x-self.width/2, self.offset_pos.y-self.height/2))

        gun_length = self.height * 1.5
        gun_center = (self.body_rect.centerx, self.body_rect.centery)
        end_x = gun_center[0] + gun_length * self.bullet_vec.normalize().x
        end_y = gun_center[1] + gun_length * self.bullet_vec.normalize().y
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
        center_x = x
        center_y = y
        gun_length = height * 1.5

        bullet.pos.x = center_x + gun_length * self.bullet_vec.normalize().x
        bullet.pos.y = center_y + gun_length * self.bullet_vec.normalize().y
        bullet.dx = self.bullet_vec.normalize().x
        bullet.dy = self.bullet_vec.normalize().y
        bullet.radius = BULLET_RADIUS
        bullet.active = True

    def shoot_bullet(self, bullet_type, alien_pos, color):
        self.bullet_vec = alien_pos - self.pos
        #bullet_vec = pygame.Vector2(bullet_vec.x, bullet_vec.y)
        vertical_vec = pygame.Vector2(0, 1)
        """if bullet_type == "test":
            self.angle = vertical_vec.angle_to(self.bullet_vec) if self.bullet_vec.x <= 0 else -1*vertical_vec.angle_to(self.bullet_vec)
        else:
            self.angle = vertical_vec.angle_to(self.bullet_vec)"""

        for bullet in self.bullet_pool:
            if not bullet.active:
                self._init_bullet(bullet, self.pos.x, self.pos.y, self.angle, self.width, self.height)
                return
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(bullet_type=bullet_type, color=color)
            self._init_bullet(bullet, self.pos.x, self.pos.y, self.angle, self.width, self.height)
            self.bullets.append(bullet)

    def update_bullets(self, target, level_id, dt):
        self.damage_dealt = False
        prev_bullet = None

        for bullet in self.bullets:
            if not bullet.active:
                continue

            if not prev_bullet:
                bullet.pos.x += bullet.dx * dt * BULLET_SPEED
                bullet.pos.y += bullet.dy * dt * BULLET_SPEED
            else:
                if prev_bullet.pos.distance_to(bullet.pos) > 50:
                    bullet.pos.x += bullet.dx * dt * BULLET_SPEED
                    bullet.pos.y += bullet.dy * dt * BULLET_SPEED
                else:
                    if prev_bullet != bullet:
                        bullet.active = False

            if target is not None:
                if (target.pos.x - BULLET_RADIUS - target.width/2 <= bullet.pos.x <= target.pos.x + target.width/2 + BULLET_RADIUS and
                    target.pos.y - BULLET_RADIUS - target.height/2 <= bullet.pos.y <= target.pos.y + target.height/2 + BULLET_RADIUS):
                    
                    hit_direction = target.pos - bullet.pos
                    
                    if hasattr(target, 'apply_pushback'):
                        target.apply_pushback(hit_direction)
                    
                    bullet.active = False
                    
                    target.health = max(0, target.health - DAMAGE_PER_HIT)
                    self.damage_dealt = True
                    self.bullet_index += 1
            
            prev_bullet = bullet

        if random.random() < 0.1:
            self.bullets = [b for b in self.bullets if b.active]
            self.bullet_pool = [b for b in self.bullets if not b.active]
        self.bullets = [b for b in self.bullets if b.active]
    
