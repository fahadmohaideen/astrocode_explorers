from levels.base_level import Level
from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT, FOR_LOOP_COLOR, DARK_GRAY
)
import pygame
import copy
import os

pygame.init()
pygame.font.init()

class Level2(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 2
        self.code_blocks = []
        self.commands["if_statement"] = {"color": FOR_LOOP_COLOR, "text": "if"}
        self.var_dict.update({"Alien near": [False, None, None],
                              "Alien Type A": [False, None, None],
                              "Alien Type B": [False, None, None],
                              "Alien Type C": [False, None, None]})

        self.value_options = [
            "Alien Type A",
            "Alien Type B",
            "Alien Type C"
        ]
        self.current_value_index = -1
        self.shoot_index = -1
        self.proceed_to_level3 = False
        self.popup_start_time = 0
        self.popup_duration_ms = 3000
        self.spawn_aliens(3)
        self.load_assets()
        super()._init_commands()

    def handle_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._process_command_clicks_recursive(mouse_pos, self.main_code)

        super().handle_events(event, mouse_pos)

    def update(self, dt, keys):
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= self.player.speed * dt
            self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += self.player.speed * dt
            self.moving = True
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= self.player.speed * dt
            self.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += self.player.speed * dt
            self.moving = True
        else:
            self.moving = False

        self.player.pos += movement


        self.var_dict["Alien near"][0] = False
        for alien_type in self.value_options:
            if alien_type in self.var_dict:
                self.var_dict[alien_type][0] = False

        for alien in self.aliens[:]:
            if alien.health <= 0 and alien.active:
                alien.active = False
                continue

            alien_near = self.player.pos.distance_to(alien.pos) < 200


            if alien_near:
                self.var_dict[alien.name][0] = True
                self.var_dict[alien.name][1] = alien
                self.var_dict["Alien near"][0] = True

        active_aliens = [alien for alien in self.aliens if alien.active]
        self.player.update_bullets(active_aliens, self.level_id, dt)

        if self.aliens_eliminated >= self.total_aliens_to_eliminate and not self.level_completed:
            self.level_completed = True
            self.current_popup = "level2_victory"

    def draw_popups(self, screen, mouse_pos, event):
        if self.current_popup == "level2_victory":

            if self.popup_start_time == 0:
                self.popup_start_time = pygame.time.get_ticks()

            popup_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
            pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=10)
            pygame.draw.rect(screen, GREEN, popup_rect, 2, border_radius=10)
            title_text = self.title_font.render("Level 2 Complete!", True, GREEN)
            screen.blit(title_text, (popup_rect.centerx - title_text.get_width() // 2, popup_rect.top + 30))

            subtitle_text = self.menu_font.render("Proceeding to Level 3...", True, WHITE)
            screen.blit(subtitle_text, (popup_rect.centerx - subtitle_text.get_width() // 2, popup_rect.centery + 10))

            if pygame.time.get_ticks() - self.popup_start_time > self.popup_duration_ms:
                self.proceed_to_level3 = True

            return

        super().draw_popups(screen, mouse_pos, event)

    def _process_command_clicks_recursive(self, mouse_pos, commands_list):
        for cmd in commands_list:
            if cmd.rect and cmd.rect.collidepoint(mouse_pos):
                if cmd.is_conditional():
                    var_box, op_box, val_box = cmd.var_box, cmd.op_box, cmd.val_box

                    if var_box.collidepoint(mouse_pos):
                        current_var = getattr(cmd, 'condition_var', None)
                        cmd.condition_var = self._cycle_value(current_var, self.var_dict)

                elif cmd.cmd_type == "shoot":
                    if cmd.shoot_type_rect and cmd.shoot_type_rect.collidepoint(mouse_pos):
                        current_index = cmd.bullet_types.index(cmd.shoot_bullet_type)
                        next_index = (current_index + 1) % len(cmd.bullet_types)
                        cmd.shoot_bullet_type = cmd.bullet_types[next_index]
                        return True

                elif cmd.is_loop():
                    if cmd.iter_box.collidepoint(mouse_pos):
                        self.editing_loop_cmd = cmd
                        cmd.editing_text = ""
                        return True
                    self.editing_loop_cmd = None

            if cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop":
                if self._process_command_clicks_recursive(mouse_pos, cmd.nested_commands):
                    return True

        return False