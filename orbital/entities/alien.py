
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
        self.prev_time = 0 
        self.health = TARGET_MAX_HEALTH 
        self.name = name
        # Initialize random direction
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        # Pushback state
        self.is_pushed = False
        self.pushback_velocity = pygame.Vector2(0, 0)
        self.pushback_duration = 0.3  # seconds
        self.pushback_timer = 0
        self.pushback_deceleration = 0.95  # How quickly the pushback slows down (0.9-0.99 for smooth deceleration)
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
        """Apply a pushback force in the opposite direction of the hit."""
        self.is_pushed = True
        self.pushback_timer = self.pushback_duration
        # Normalize the hit direction and scale by force
        if hit_direction.length() > 0:
            self.pushback_velocity = hit_direction.normalize() * force
        else:
            # If hit direction is zero (shouldn't happen), push back in a random direction
            self.pushback_velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * force
    
    def update_pushback(self, dt):
        """Update the pushback effect."""
        if self.pushback_timer > 0:
            # Apply pushback velocity
            self.pos += self.pushback_velocity * dt
            
            # Decelerate the pushback
            self.pushback_velocity *= self.pushback_deceleration
            
            # Update timer
            self.pushback_timer -= dt
            
            # If pushback is almost done, end it
            if self.pushback_timer <= 0 or self.pushback_velocity.length() < 5.0:
                self.pushback_timer = 0
                self.is_pushed = False
                self.pushback_velocity = pygame.Vector2(0, 0)
    
    def move_towards_player(self, player_pos, dt, boundary_width, boundary_height):
        """Move towards the player if within detection range."""
        # Calculate direction to player
        direction_to_player = pygame.Vector2(player_pos) - self.pos
        distance_to_player = direction_to_player.length()
        
        # If player is within 300 units but more than 75 units away, chase the player
        if 100 < distance_to_player < 300:
            # Normalize direction and set speed
            chase_speed = 70  # Slightly faster when chasing
            self.direction = direction_to_player.normalize()
            
            # Move the alien
            new_pos = self.pos + self.direction * chase_speed * dt
            
            # Keep within boundaries
            new_pos.x = max(0, min(new_pos.x, boundary_width))
            new_pos.y = max(0, min(new_pos.y, boundary_height))
            
            # Update position
            self.pos = new_pos
            
            # Update angle to face the player
            if self.direction.length() > 0:
                self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
                
        # If player is within 75 units, stop moving but still face the player
        elif distance_to_player <= 100 and distance_to_player > 0:
            # Just update the angle to face the player without moving
            self.direction = direction_to_player.normalize()
            if self.direction.length() > 0:
                self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
                
        # If player is too far, move randomly
        else:
            # Move randomly
            chase_speed = 50
            if random.random() < 0.01:  # 1% chance to change direction each frame
                self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.direction.length() > 0:
                    self.direction = self.direction.normalize()
            
            # Move the alien
            new_pos = self.pos + self.direction * chase_speed * dt
            
            # Keep within boundaries
            new_pos.x = max(0, min(new_pos.x, boundary_width))
            new_pos.y = max(0, min(new_pos.y, boundary_height))
            
            # Update position and angle
            self.pos = new_pos
            if self.direction.length() > 0:
                self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
    
    def move_randomly(self, dt, boundary_width, boundary_height, player_pos=None):
        """Move the alien, with optional player chasing."""
        # If being pushed, only update pushback movement
        if self.is_pushed:
            self.update_pushback(dt)
            return
            
        # If player position is provided, use the chasing logic
        if player_pos is not None:
            self.move_towards_player(player_pos, dt, boundary_width, boundary_height)
            return
            
        # Original random movement code (kept for backward compatibility)
        if random.random() < 0.01:  # 1% chance to change direction each frame
            self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
        
        # Move the alien
        speed = 50
        new_pos = self.pos + self.direction * speed * dt
        
        # Keep within boundaries
        new_pos.x = max(0, min(new_pos.x, boundary_width))
        new_pos.y = max(0, min(new_pos.y, boundary_height))
        
        # Update position and angle
        self.pos = new_pos
        if self.direction.length() > 0:
            self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
    
    def shoot_alien_bullets(self, player, dt):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.prev_time >= 500:  # Original cooldown
            self.shoot_bullet(None, player.pos, (255, 100, 255))
            self.prev_time = curr_time