
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
        super().__init__(x, y, 60, 60)
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(self.x + self.width/2, self.y + self.height/2)
        self.offset_pos = self.pos
        self.angle = 90
        self.body_rect = pygame.Rect(self.offset_pos.x - self.width/2, self.offset_pos.y - self.height/2,
                                   self.width, self.height)
        self.shape_options = ["circle", "square", "triangle"]
        self.prev_time = 0 
        self.health = TARGET_MAX_HEALTH 
        self.name = name
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.is_pushed = False
        self.pushback_velocity = pygame.Vector2(0, 0)
        self.pushback_duration = 0.3
        self.pushback_timer = 0
        self.pushback_deceleration = 0.95
    """def draw_health_bar(self, surface):
        
        bar_width = self.width
        bar_height = 10
        bar_x = self.x
        bar_y = self.y - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)"""

    def apply_pushback(self, hit_direction, force=200.0):
        self.is_pushed = True
        self.pushback_timer = self.pushback_duration
        if hit_direction.length() > 0:
            self.pushback_velocity = hit_direction.normalize() * force
        else:
            self.pushback_velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * force
    
    def update_pushback(self, dt):
        if self.pushback_timer > 0:
            self.pos += self.pushback_velocity * dt
            self.pushback_velocity *= self.pushback_deceleration
            
            self.pushback_timer -= dt
            
            if self.pushback_timer <= 0 or self.pushback_velocity.length() < 5.0:
                self.pushback_timer = 0
                self.is_pushed = False
                self.pushback_velocity = pygame.Vector2(0, 0)
    
    def move_towards_player(self, player_pos, dt, boundary_width, boundary_height):
        direction_to_player = player_pos - self.pos
        distance_to_player = direction_to_player.length()
        
        if 100 < distance_to_player < 300:
            chase_speed = 70
            self.direction = direction_to_player.normalize()
            
            new_pos = self.pos + self.direction * chase_speed * dt
            
            new_pos.x = max(0, min(new_pos.x, boundary_width))
            new_pos.y = max(0, min(new_pos.y, boundary_height))
            
            self.pos = new_pos
            
            if self.direction.length() > 0:
                self.bullet_vec = self.direction
                
        elif distance_to_player <= 100 and distance_to_player > 0:
            self.direction = direction_to_player.normalize()
            if self.direction.length() > 0:
                self.bullet_vec = self.direction
                
        else:
            chase_speed = 50
            if random.random() < 0.01:
                self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.direction.length() > 0:
                    self.direction = self.direction.normalize()
            
            new_pos = self.pos + self.direction * chase_speed * dt
            
            new_pos.x = max(0, min(new_pos.x, boundary_width))
            new_pos.y = max(0, min(new_pos.y, boundary_height))
            
            self.pos = new_pos
            if self.direction.length() > 0:
                self.bullet_vec = self.direction
    
    def move_randomly(self, dt, boundary_width, boundary_height, player_pos=None):
        if self.is_pushed:
            self.update_pushback(dt)
            return
            
        if player_pos is not None:
            self.move_towards_player(player_pos, dt, boundary_width, boundary_height)
            return
            
        if random.random() < 0.01:
            self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
        
        speed = 50
        new_pos = self.pos + self.direction * speed * dt
        
        new_pos.x = max(0, min(new_pos.x, boundary_width))
        new_pos.y = max(0, min(new_pos.y, boundary_height))
        
        self.pos = new_pos
        if self.direction.length() > 0:
            self.bullet_vec = self.direction
    
    def shoot_alien_bullets(self, player, dt):
        curr_time = pygame.time.get_ticks()
        time_since_last_shot = curr_time - self.prev_time
        print(f"[DEBUG] shoot_alien_bullets - curr_time: {curr_time}, prev_time: {self.prev_time}, time_since_last_shot: {time_since_last_shot}")
        if time_since_last_shot >= 500:
            print("[DEBUG] Attempting to shoot bullet")
            try:
                self.shoot_bullet("test", player.pos, (255, 100, 255))
                print(f"[DEBUG] After shoot_bullet, bullets: {len(self.bullets)}")
                self.prev_time = curr_time
            except Exception as e:
                print(f"[ERROR] Error in shoot_bullet: {e}")
                raise