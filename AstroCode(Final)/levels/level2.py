from levels.base_level import Level
from core.constants import (
    WIDTH, HEIGHT, ORANGE, BLUE, GREEN, RED, WHITE, CYAN,
    BULLET_RADIUS, BULLET_SPEED, PLAYER_MAX_HEALTH, TARGET_MAX_HEALTH, DAMAGE_PER_HIT, FOR_LOOP_COLOR, DARK_GRAY
)
import pygame
import copy
import os
import random
from ui.button import Button

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
        self.show_briefing = True
        self.briefing_start_time = 0
        self.briefing_duration_ms = 8000

        alien_types_to_spawn = list(self.value_options)
        random.shuffle(alien_types_to_spawn)
        self.spawn_aliens_with_types(alien_types_to_spawn)

        self.load_assets()
        super()._init_commands()

    def load_assets(self):
        super().load_assets()
        try:
            ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
            mystery_image_path = os.path.join(ASSETS_PATH, "mystery_alien.png")
            mystery_img = pygame.transform.scale(
                pygame.image.load(mystery_image_path).convert_alpha(),
                (60, 60)
            )
            for alien_type in self.value_options:
                if alien_type in self.var_dict:
                    self.var_dict[alien_type][2] = mystery_img
        except Exception as e:
            print(f"Error loading mystery alien asset for Level 2: {e}")

    def handle_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._process_command_clicks_recursive(mouse_pos, self.main_code)
        super().handle_events(event, mouse_pos)

    def update(self, dt, keys):
        if self.player.health <= 0 and not self.player.is_dying:
            self.player.is_dying = True
            print("Player has been defeated by penalties!")
            self.current_popup = "failure"


        if self.player.is_dying:
            return
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

        if self.current_popup == "failure":
            popup_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
            pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=10)
            pygame.draw.rect(screen, RED, popup_rect, 2, border_radius=10)


            text = self.title_font.render("Mission Failed!", True, RED)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 30))


            menu_btn = Button(popup_rect.centerx - 135, popup_rect.bottom - 100, 275, 50,
                              "Return to Menu", BLUE, CYAN, self.menu_font)
            menu_btn.draw(screen)
            if menu_btn.is_clicked(mouse_pos, event):
                self.exit_to_levels = True
            return

        super().draw_popups(screen, mouse_pos, event)

    def draw_level_intro(self, surface):
        """Draws a simple, timed line of text at the top of the screen."""

        if not self.show_briefing:
            return

        current_time = pygame.time.get_ticks()
        if self.briefing_start_time == 0:
            self.briefing_start_time = current_time

        if current_time - self.briefing_start_time > self.briefing_duration_ms:
            self.show_briefing = False
            return


        instruction = "Mission: Use 'if' to scan alien type, then 'shoot' with the matching bullet! You have 3 attempts."


        font = pygame.font.Font(None, 24)


        text_surface = font.render(instruction, True, WHITE)


        text_rect = text_surface.get_rect(center=(WIDTH // 2, 200))

        surface.blit(text_surface, text_rect)

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