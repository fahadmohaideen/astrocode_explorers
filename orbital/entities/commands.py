import pygame
import math
import copy

from core.constants import (
    WHITE, BLACK, CYAN, ORANGE, BLUE, GREEN, FOR_LOOP_COLOR
)
from entities.bullet_shapes import Circle, Square, Triangle

class Command:
    def __init__(self, cmd_type, iterations=1, nested_commands=None, rect=None, conditions=None, condition_var=None,
                 condition_op=None, condition_val=None, editing_condition_part=None, code_font=None):
        self.cmd_type = cmd_type
        self.code_font = code_font
        self.iterations = iterations
        self.conditions = conditions if conditions is not None else {}
        self.nested_commands = nested_commands if nested_commands is not None else []
        self.rect = rect
        self.condition_var = condition_var
        self.condition_op = condition_op
        self.condition_val = condition_val
        self.editing_condition_part = editing_condition_part
        self.shoot_target_shape = Circle(0, 0, 8, WHITE)
        self.shoot_target_box_rect = None

        self.color = self._get_color()
        self.text = self._get_text()

    def _get_color(self):
        colors = {
            "move": (0, 100, 200),
            "turn_left": (200, 100, 0),
            "turn_right": (20, 100, 0),
            "reverse": (250, 100, 0),
            "shoot": (250, 100, 0),
            "for_loop": FOR_LOOP_COLOR
        }
        return colors.get(self.cmd_type, (100, 100, 100))

    def _get_text(self):
        texts = {
            "move": "Move Forward",
            "turn_left": "Turn Left",
            "turn_right": "Turn Right",
            "reverse": "Reverse",
            "shoot": "Shoot",
            "for_loop": "For Loop",
            "if_statement": "if block",
            "while_loop": "while"
        }
        return texts.get(self.cmd_type, "Unknown")

    def is_loop(self):
        return self.cmd_type == "for_loop"

    def is_conditional(self):
        return self.cmd_type == "if_statement"

    def draw(self, surface, x, y, width, indent=0, is_nested=False):
        if self.rect is None:
            self.rect = pygame.Rect(
                x + indent,
                y,
                width - indent,
                25 if not self.is_loop() else 40
            )
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)

        if self.is_loop() or self.is_conditional() or self.cmd_type == "while_loop":
            if self.is_loop():
                self._draw_loop_header(surface)
            elif self.is_conditional():
                self._draw_conditional_header("if", surface)
            else:
                self._draw_regular_command(surface)

            nested_y = y + 40
            for nested_cmd in self.nested_commands:
                nested_height = nested_cmd.draw(
                    surface,
                    x,
                    nested_y,
                    width - 20,
                    indent + 20,
                    True
                )
                nested_y += nested_height

            self.rect.height = max(40, nested_y - y)
        elif self.cmd_type == "shoot":
            self._draw_shoot_command_content(surface)

        else:
            self._draw_regular_command(surface)

        return self.rect.height

    def _draw_regular_command(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)
        text = self.code_font.render(self.text, True, WHITE)
        surface.blit(text, (self.rect.x + 5, self.rect.y + 5))

    def _draw_loop_header(self, surface):
        header_text = "Repeat"
        text_surf = self.code_font.render(header_text, True, WHITE)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

        box_start_x = self.rect.x + 10 + text_surf.get_width() + 10
        box_width = 60
        box_height = 20
        box_y = self.rect.y + 5
        iter_box = pygame.Rect(box_start_x, box_y, box_width, box_height)

        pygame.draw.rect(surface, BLACK, iter_box)
        pygame.draw.rect(surface, WHITE, iter_box, 1)

        iter_text = str(self.iterations)
        iter_surf = self.code_font.render(iter_text, True, WHITE)
        iter_rect = iter_surf.get_rect(center=iter_box.center)
        surface.blit(iter_surf, iter_rect)

        times_text = "times"
        text_surf_1 = self.code_font.render(times_text, True, WHITE)
        surface.blit(text_surf_1, (box_start_x + box_width + 10, self.rect.y + 10))

    def _draw_conditional_header(self, txt, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)
        if_text = self.code_font.render(txt, True, WHITE)
        surface.blit(if_text, (self.rect.x + 10, self.rect.y + 10))

        box_start_x = self.rect.x + 10 + if_text.get_width() + 10
        box_width = 60
        op_width = 30
        box_height = 20
        box_y = self.rect.y + 5

        var_box = pygame.Rect(box_start_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, BLACK, var_box)
        pygame.draw.rect(surface, WHITE, var_box, 1)
        if hasattr(self, 'condition_var') and self.condition_var:
            var_text = self.code_font.render(self.condition_var, True, WHITE)
            surface.blit(var_text, (var_box.x + 5, var_box.y + 3))

        op_box = pygame.Rect(box_start_x + box_width + 5, box_y, op_width, box_height)
        pygame.draw.rect(surface, BLACK, op_box)
        pygame.draw.rect(surface, WHITE, op_box, 1)
        if hasattr(self, 'condition_op') and self.condition_op:
            op_text = self.code_font.render(self.condition_op, True, WHITE)
            surface.blit(op_text, (op_box.x + 5, op_box.y + 3))

        val_box = pygame.Rect(box_start_x + box_width + op_width + 10, box_y, box_width, box_height)
        pygame.draw.rect(surface, BLACK, val_box)
        pygame.draw.rect(surface, WHITE, val_box, 1)
        if hasattr(self, 'condition_val') and self.condition_val:
            #val_text = code_font.render(str(self.condition_val), True, WHITE)
            self.condition_val.x = val_box.centerx
            self.condition_val.y = val_box.centery
            self.condition_val.draw(surface)

        if hasattr(self, 'editing_condition_part'):
            cursor_box = {
                'var': var_box,
                'op': op_box,
                'val': val_box
            }.get(self.editing_condition_part)

            if cursor_box:
                pygame.draw.rect(surface, CYAN, cursor_box, 2)

    def _draw_shoot_command_content(self, surface):
        shoot_text = self.code_font.render(self.text, True, WHITE)
        surface.blit(shoot_text, (self.rect.x + 5, self.rect.y + 5))
        box_width = 30
        box_height = 20
        box_x = self.rect.x + 5 + shoot_text.get_width() + 10
        box_y = self.rect.y + 5

        self.shoot_target_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        pygame.draw.rect(surface, BLACK, self.shoot_target_box_rect)
        pygame.draw.rect(surface, WHITE, self.shoot_target_box_rect, 1)

        if self.shoot_target_shape:
            self.shoot_target_shape.x = self.shoot_target_box_rect.centerx
            self.shoot_target_shape.y = self.shoot_target_box_rect.centery
            self.shoot_target_shape.draw(surface)