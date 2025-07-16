# Level 2 logic
from levels.base_level import Level
from core.constants import FOR_LOOP_COLOR
import pygame
import copy
import os

pygame.init()
pygame.font.init()

class Level2(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        #self.curr_nearest_alien = None
        self.level_id = 2
        # Level2 specific initialization
        self.code_blocks = []
        #self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        self.commands["if_statement"] = {"color": FOR_LOOP_COLOR, "text": "if"}
        self.var_dict.update({"Alien near": [False, None, None],
                            "Alien Type A": [False, None, None],
                            "Alien Type B": [False, None, None],
                            "Alien Type C": [False, None, None]})
        self.value_options = [
            "Type A",  # Radius 8 for a small circle
            "Type B",  # Size 16 for a small square
            "Type C"  # Size 16 for a small triangle (approximate height)
        ]
        self.current_value_index = -1
        self.shoot_index = -1
        self.spawn_aliens(3)
        self.load_assets()
        super()._init_commands()

    def handle_events(self, event, mouse_pos):
        # Handle condition boxes differently in Level 3
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

        # Reset proximity flags at start of each frame
        self.var_dict["Alien near"][0] = False
        for alien in self.aliens:
            alien_near = self.player.pos.distance_to(alien.pos) < 200

            # Update individual alien tracking
            self.var_dict[alien.name][0] = alien_near
            self.var_dict[alien.name][1] = alien if alien_near else None

            # OR condition: if ANY alien is near
            if alien_near:
                self.var_dict["Alien near"][0] = True
                self.curr_nearest_alien = alien  # Track the nearest one

        for alien in self.aliens:
            self.player.update_bullets(alien, self.level_id, dt)

        super().update(dt)

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
                    var_box, op_box, val_box = cmd.var_box, cmd.op_box, cmd.val_box

                    if var_box.collidepoint(mouse_pos):
                        # Cycle through variables
                        current_var = getattr(cmd, 'condition_var', None)
                        cmd.condition_var = self._cycle_value(current_var, self.var_dict)
                        #cmd.editing_condition_part = None  # Not typing, just cycling

                    """elif op_box.collidepoint(mouse_pos):
                        # Cycle through operators
                        current_op = getattr(cmd, 'condition_op', None)
                        cmd.condition_op = self._cycle_value(current_op, self.op_dict)
                        #cmd.editing_condition_part = None  # Not typing, just cycling

                    elif val_box.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.condition_val = copy.deepcopy(self.value_options[self.current_value_index])
                        return True  # Click handled"""

                # Handle 'Shoot' Command clicks (specific to Level 3)
                elif cmd.cmd_type == "shoot":
                    if cmd.shoot_bullet_type_box and cmd.shoot_bullet_type_box.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.shoot_bullet_type = copy.deepcopy(self.value_options[self.current_value_index])
                        return True  # Click handled

                elif cmd.is_loop():
                    if cmd.iter_box.collidepoint(mouse_pos):
                        self.editing_loop_cmd = cmd
                        cmd.editing_text = ""
                        return True
                    self.editing_loop_cmd = None


            # Recursively check nested commands if this command is a loop or conditional
            if cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop":
                # If a click is handled by a nested command, propagate True
                if self._process_command_clicks_recursive(mouse_pos, cmd.nested_commands):
                    return True  # Click handled by a nested command

        return False  # No click handled in this list or its descendants