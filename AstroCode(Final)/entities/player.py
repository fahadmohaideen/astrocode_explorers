import pygame
import math
import random
import os
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
        self.bullets = []
        self.max_bullets = 50
        self.bullet_pool = []
        self.damage_dealt = False
        self.health = PLAYER_MAX_HEALTH
        self.last_hit_bullet_shape = None
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 90
        try:
            assets_path = os.path.join("levels", "assets")
            self.gun_image_original = pygame.image.load(os.path.join(assets_path, "gun.png")).convert_alpha()
            self.gun_image_original = pygame.transform.scale(self.gun_image_original, (60, 20))
        except Exception as e:
            print(f"Error loading gun.png: {e}")
            self.gun_image_original = None

    def draw_player(self, surface, img):
        if self.is_dying:
            self.death_animation_timer += 1
            if self.death_animation_timer > self.death_animation_duration:
                self.death_animation_timer = self.death_animation_duration

            progress = self.death_animation_timer / self.death_animation_duration
            alpha = int(255 * (1 - progress))
            scale = 1 - progress

            faded_img = img.copy()
            faded_img.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            scaled_img = pygame.transform.scale(
                faded_img,
                (int(self.width * scale), int(self.height * scale))
            )


            death_rect = scaled_img.get_rect(center=self.offset_pos)
            surface.blit(scaled_img, death_rect)
            return


        self.body_rect = pygame.Rect(self.offset_pos.x - self.width / 2, self.offset_pos.y - self.height / 2,
                                     self.width, self.height)
        surface.blit(img, self.body_rect.topleft)

        if self.gun_image_original:
            rotated_gun = pygame.transform.rotate(self.gun_image_original, self.angle)
            gun_rect = rotated_gun.get_rect(center=self.body_rect.center)
            surface.blit(rotated_gun, gun_rect.topleft)


    def draw_health_bar(self, surface):
        bar_width = self.width
        bar_height = 10
        bar_x = self.offset_pos.x - self.width/2
        bar_y = self.offset_pos.y - self.height/2 - bar_height - 5

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.health / PLAYER_MAX_HEALTH) * bar_width
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

    def shoot_bullet(self, bullet_type, direction, color):
        spawn_pos = self.pos.copy()

        bullet = Bullet(
            x=spawn_pos.x,
            y=spawn_pos.y,
            dx=direction.x * BULLET_SPEED,
            dy=direction.y * BULLET_SPEED,
            bullet_type=bullet_type,
            color=color
        )
        self.bullets.append(bullet)
        return bullet


    def update_bullets(self, targets, level_id, dt, camera_offset=None):
            if not isinstance(targets, (list, tuple)):
                targets = [targets] if targets else []

            for bullet in self.bullets[:]:
                if not bullet.active:
                    continue

                bullet.pos.x += bullet.dx * dt
                bullet.pos.y += bullet.dy * dt

                player_to_bullet = bullet.pos - self.pos
                if player_to_bullet.length() > 2000:
                    bullet.active = False
                    continue

                for target in targets:
                    if not hasattr(target, 'active') or not target.active or getattr(target, 'health', 1) <= 0:
                        continue

                    distance = bullet.pos.distance_to(target.pos)
                    collision_threshold = getattr(target, 'width', 50) / 2 + bullet.radius

                    if distance < collision_threshold:
                        if not getattr(target, 'shielded', False):
                            should_damage = False

                            if level_id == 1:
                                should_damage = True


                            else:
                                alien_type = getattr(target, 'name', None)
                                if bullet.bullet_type == alien_type:
                                    should_damage = True
                                else:
                                    print(
                                        f"INCORRECT HIT. Bullet '{bullet.bullet_type}' does not damage Alien '{alien_type}'.")


                            if should_damage:
                                target.health -= DAMAGE_PER_HIT
                                print(f"HIT! Target health is now: {target.health}")


                        else:

                            print(f"HIT FAILED! Alien '{getattr(target, 'name', 'Unknown')}' shield is active.")


                        bullet.active = False
                        break


            self.bullets = [bullet for bullet in self.bullets if bullet.active]



