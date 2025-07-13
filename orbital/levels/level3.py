
from levels.level2 import Level2
from entities.bullet_shapes import Circle, Square, Triangle
from core.constants import WHITE, FOR_LOOP_COLOR
import pygame
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
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        self.commands["if_statement"] = {"color": FOR_LOOP_COLOR, "text": "if"}
        super()._init_commands()

    def update(self, dt, keys):
        super().update(dt, keys)
        for alien in self.var_dict.keys():
            if self.var_dict[alien][1]:
                self.var_dict[alien][1].shoot_alien_bullets(self.player, dt)

        for alien in self.aliens:
            alien.update_bullets(self.player, 0, dt)

    """def handle_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:

                self._process_command_clicks_recursive(mouse_pos, self.main_code)


        super().handle_events(event, mouse_pos)

    def _process_command_clicks_recursive(self, mouse_pos, commands_list):
        
        for cmd in commands_list:
            if cmd.rect and cmd.rect.collidepoint(mouse_pos):
                if cmd.is_conditional():
                    var_box, op_box, val_box = cmd.var_box, cmd.op_box, cmd.val_box

                    if var_box.collidepoint(mouse_pos):
                        current_var = getattr(cmd, 'condition_var', None)
                        cmd.condition_var = self._cycle_value(current_var, self.var_dict)

                    elif op_box.collidepoint(mouse_pos):
                        current_op = getattr(cmd, 'condition_op', None)
                        cmd.condition_op = self._cycle_value(current_op, self.op_dict)

                    elif val_box.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.condition_val = copy.deepcopy(self.value_options[self.current_value_index])
                        return True

                elif cmd.cmd_type == "shoot":
                    if cmd.shoot_target_box_rect and cmd.shoot_target_box_rect.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.shoot_target_shape = copy.deepcopy(self.value_options[self.current_value_index])
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

        return False """