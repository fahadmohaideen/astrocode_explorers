
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
        # Initialize Player with proper dimensions first
        super().__init__(x, y, 60, 60)  # width=60, height=60
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
        direction_to_player = player_pos - self.pos
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
                # Calculate angle in degrees where 0 is up, 90 is right, 180 is down, 270 is left
                #self.angle = math.degrees(math.atan2(-self.direction.x, -self.direction.y))
                self.bullet_vec = self.direction
                
        # If player is within 75 units, stop moving but still face the player
        elif distance_to_player <= 100 and distance_to_player > 0:
            # Just update the angle to face the player without moving
            self.direction = direction_to_player.normalize()
            if self.direction.length() > 0:
                # Calculate angle in degrees where 0 is up, 90 is right, 180 is down, 270 is left
                self.bullet_vec = self.direction
                
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
                # Calculate angle in degrees where 0 is up, 90 is right, 180 is down, 270 is left
                self.bullet_vec = self.direction
    
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
                # Calculate angle in degrees where 0 is up, 90 is right, 180 is down, 270 is left 
                self.bullet_vec = self.direction
    
    def shoot_alien_bullets(self, player, dt):
        curr_time = pygame.time.get_ticks()
        time_since_last_shot = curr_time - self.prev_time
        print(f"[DEBUG] shoot_alien_bullets - curr_time: {curr_time}, prev_time: {self.prev_time}, time_since_last_shot: {time_since_last_shot}")
        if time_since_last_shot >= 500:  # 500ms cooldown
            print("[DEBUG] Attempting to shoot bullet")
            try:
                self.shoot_bullet("test", player.pos, (255, 100, 255))
                print(f"[DEBUG] After shoot_bullet, bullets: {len(self.bullets)}")
                self.prev_time = curr_time
            except Exception as e:
                print(f"[ERROR] Error in shoot_bullet: {e}")
                raise