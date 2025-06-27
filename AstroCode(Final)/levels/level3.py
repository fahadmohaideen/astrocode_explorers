# Level 3 logic
from levels.base_level import Level
from entities.bullet_shapes import Circle, Square, Triangle
from core.constants import WHITE, FOR_LOOP_COLOR
import pygame
import copy

pygame.init()
pygame.font.init()

class Level3(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 3
        self.code_font = code_font
        self.title_font = title_font
        # Level2 specific initialization
        self.code_blocks = []
        self.value_options = [
            Circle(0, 0, 8, WHITE),  # Radius 8 for a small circle
            Square(0, 0, 16, WHITE),  # Size 16 for a small square
            Triangle(0, 0, 16, WHITE)  # Size 16 for a small triangle (approximate height)
        ]
        self.current_value_index = -1
        self.shoot_index = -1
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        self.commands["if_statement"] = {"color": FOR_LOOP_COLOR, "text": "if"}
        super()._init_commands()

    def handle_events(self, event, mouse_pos):
        # Handle condition boxes differently in Level 3
        if event.type == pygame.MOUSEBUTTONDOWN:
            for cmd in self.main_code:
                if cmd.is_conditional() and cmd.rect.collidepoint(mouse_pos):
                    var_box, op_box, val_box = self._get_condition_boxes(cmd)
                    """self.value_options.append(
                        Circle(val_box.centerx, val_box.centery, int(0.15 * (val_box.right - val_box.left)), WHITE))
                    self.value_options.append(
                        Square(val_box.centerx - 10, val_box.centery - 10, int(0.3 * (val_box.right - val_box.left)),
                               WHITE))
                    self.value_options.append(Triangle([(val_box.bottomleft[0] + 15, val_box.bottomleft[1] - 5),
                                                        (val_box.midtop[0], val_box.midtop[1] + 5),
                                                        (val_box.bottomright[0] - 15, val_box.bottomright[1] - 5)],
                                                       WHITE))"""

                    if val_box.collidepoint(mouse_pos):
                        # Level 3 specific: cycle through predefined values
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.condition_val = copy.deepcopy(self.value_options[self.current_value_index])
                        return
                elif cmd.cmd_type == "shoot" and cmd.rect.collidepoint(mouse_pos):
                    # Ensure the shoot_target_box_rect has been calculated (i.e., the command was drawn)
                    if cmd.shoot_target_box_rect and cmd.shoot_target_box_rect.collidepoint(mouse_pos):
                        # Cycle through predefined values for shoot_target_shape
                        # Reusing current_value_index for simplicity. If you want independent cycles,
                        # you'd need a separate self.current_shoot_shape_index
                        self.shoot_index = (self.shoot_index + 1) % len(self.value_options)
                        cmd.shoot_target_shape = copy.deepcopy(self.value_options[self.shoot_index])
                        return  # Exit after handling click

            self._process_command_clicks_recursive(mouse_pos, self.main_code)

        # For other events or non-Level3 behavior, use parent's handling
        super().handle_events(event, mouse_pos)

    def _process_command_clicks_recursive(self, mouse_pos, commands_list):
        """
        Recursively processes mouse clicks on commands and their nested commands,
        handling conditional value boxes and shoot target shapes.
        """
        for cmd in commands_list:
            # Check if the click is within the main rectangle of the command
            if cmd.rect and cmd.rect.collidepoint(mouse_pos):
                # Handle Conditional Command (if_statement) clicks
                if cmd.is_conditional():
                    # _get_condition_boxes needs to be robust enough to work for any cmd
                    # regardless of nesting level, relying on cmd.rect.
                    var_box, op_box, val_box = self._get_condition_boxes(cmd)
                    if val_box.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.condition_val = copy.deepcopy(self.value_options[self.current_value_index])
                        return True  # Click handled

                # Handle 'Shoot' Command clicks (specific to Level 3)
                elif cmd.cmd_type == "shoot":
                    if cmd.shoot_target_box_rect and cmd.shoot_target_box_rect.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.shoot_target_shape = copy.deepcopy(self.value_options[self.current_value_index])
                        return True  # Click handled

            # Recursively check nested commands if this command is a loop or conditional
            if cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop":
                # If a click is handled by a nested command, propagate True
                if self._process_command_clicks_recursive(mouse_pos, cmd.nested_commands):
                    return True  # Click handled by a nested command

        return False  # No click handled in this list or its descendants