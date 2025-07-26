from levels.level2 import Level2
from core.constants import WHITE, FOR_LOOP_COLOR, WIDTH, HEIGHT, DARK_GRAY, RED, BLUE, CYAN, DAMAGE_PER_HIT
import pygame
from ui.button import Button
import copy
import os

pygame.init()
pygame.font.init()

class Level3(Level2):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 3
        self.code_font = code_font
        self.title_font = title_font
        self.code_blocks = []
        """self.value_options = [
            Circle(0, 0, 8, WHITE),
            Square(0, 0, 16, WHITE),
            Triangle(0, 0, 16, WHITE)
        ]
        self.current_value_index = -1
        self.shoot_index = -1"""
        self.run_click_limit = 5
        self.run_clicks_used = 0
        self.show_briefing = True
        self.briefing_start_time = 0
        self.briefing_duration_ms = 8000
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        self.commands["if_statement"] = {"color": FOR_LOOP_COLOR, "text": "if"}
        super()._init_commands()
        for alien in self.aliens:
            alien.shielded = True
        self.load_assets()

    def draw_level_intro(self, surface):
        if not self.show_briefing:
            return

        current_time = pygame.time.get_ticks()
        if self.briefing_start_time == 0:
            self.briefing_start_time = current_time

        if current_time - self.briefing_start_time > self.briefing_duration_ms:
            self.show_briefing = False
            return


        instruction = "Mission: Run attempts are limited! Use the 'for loop' for efficiency."

        font = pygame.font.Font(None, 28)
        text_surface = font.render(instruction, True, WHITE)

        text_rect = text_surface.get_rect(center=(WIDTH // 2, 200))

        surface.blit(text_surface, text_rect)

    def load_assets(self):

        super(Level2, self).load_assets()


    def update(self, dt, keys):
        if self.player.health <= 0 and not self.player.is_dying:
            self.player.is_dying = True
            print("Player has been defeated!")
            return

        if self.player.is_dying:
            return

        super().update(dt, keys)
        for alien in self.aliens:
            if alien.active:
                alien.update_shield()
                alien.shoot_at_player(self.player, dt)
                alien.update_bullets(self.player, self.level_id, dt)

    def draw_popups(self, screen, mouse_pos, event):

            if self.current_popup != "failure":
                remaining = self.run_click_limit - self.run_clicks_used
                counter_text = f"Run Attempts Remaining: {remaining}"

                font = self.menu_font
                text_surface = font.render(counter_text, True, WHITE)


                text_rect = text_surface.get_rect(topright=(WIDTH - 540, 100))


                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(screen, DARK_GRAY, bg_rect, border_radius=5)
                pygame.draw.rect(screen, CYAN, bg_rect, 2, border_radius=5)

                screen.blit(text_surface, text_rect)

            if self.player.is_dying and self.player.death_animation_timer >= self.player.death_animation_duration:
                self.current_popup = "failure"

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

            else:
                super().draw_popups(screen, mouse_pos, event)

    def _process_command_clicks_recursive(self, mouse_pos, commands_list):
        for cmd in commands_list:
            if cmd.rect and cmd.rect.collidepoint(mouse_pos):
                if cmd.is_conditional():
                    var_box, op_box, val_box = cmd.var_box, cmd.op_box, cmd.val_box
                    if var_box.collidepoint(mouse_pos):
                        current_var = getattr(cmd, 'condition_var', None)
                        cmd.condition_var = self._cycle_value(current_var, self.var_dict)
                        return True

                elif cmd.cmd_type == "shoot":
                    if cmd.shoot_type_rect and cmd.shoot_type_rect.collidepoint(mouse_pos):
                        current_index = cmd.bullet_types.index(cmd.shoot_bullet_type)
                        next_index = (current_index + 1) % len(cmd.bullet_types)
                        cmd.shoot_bullet_type = cmd.bullet_types[next_index]
                        return True

                elif cmd.is_loop():
                    if cmd.iter_box and cmd.iter_box.collidepoint(mouse_pos):
                        cmd.iterations += 1
                        if cmd.iterations > 4:
                            cmd.iterations = 1
                        print(f"Loop iterations set to: {cmd.iterations}")
                        return True

            if cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop":
                if self._process_command_clicks_recursive(mouse_pos, cmd.nested_commands):
                    return True

        return False

    def handle_events(self, event, mouse_pos):
        if self.run_button.is_clicked(mouse_pos, event):
            if self.run_clicks_used < self.run_click_limit:

                self.run_clicks_used += 1
                print(f"Run button clicked. Uses remaining: {self.run_click_limit - self.run_clicks_used}")

                self.code_editor = False
                self.game_view = True
                self.cmd_gen = self.execute_commands(self.main_code, None)
                self._update_nearest_alien()
            else:
                print("Run limit exceeded! Mission failed.")
                self.current_popup = "failure"
            return


        super().handle_events(event, mouse_pos)