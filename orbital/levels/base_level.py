# Base class shared by all levels
import pygame
import math
import collections
import copy

from core.constants import (
    WIDTH, HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, CYAN, ORANGE,
    FOR_LOOP_COLOR, BULLET_RADIUS, TARGET_MAX_HEALTH, PLAYER_MAX_HEALTH,
    DAMAGE_PER_HIT, PLAYER_AWARENESS_RANGE, COMMAND_DELAY_MS, screen
)
#from game1 import code_font
from ui.button import Button
from entities.player import Player
from entities.alien import Alien
from entities.bullet import Bullet
from entities.commands import Command
from entities.bullet_shapes import Circle, Square, Triangle# Import shape classes

pygame.init()
pygame.font.init()

class Level:
    def __init__(self, code_font, title_font, menu_font):
        # Common initialization code
        self.code_font = code_font
        self.title_font = title_font
        self.menu_font = menu_font
        self.battlefield = pygame.Rect(50, 150, 400, 300)
        self.target = pygame.Rect(60, 160, 60, 60)
        self.player_size = 20
        self.player_pos = [
            self.battlefield.centerx - self.player_size // 2,
            self.battlefield.bottom - self.player_size - 5
        ]
        self.player_angle = 0
        self.dragging = None
        self.main_code = []
        self.bullets = []
        self.bullet_pool = []  # Recycled bullets
        self.bullet_options = []
        self.max_bullets = 100  # Adjust based on needs
        self.code_blocks = []
        self.target_health = TARGET_MAX_HEALTH
        self.last_shot_time = 0
        self.shot_cooldown = 0
        self.code_area = pygame.Rect(500, 100, 250, 400)
        self.commands_area = pygame.Rect(50, 5, 700, 50)
        self.run_button = Button(637, 550, 100, 40, "Run", GREEN, (0, 200, 0), self.menu_font)
        self.reset_button = Button(513, 550, 100, 40, "Reset", RED, (200, 0, 0), self.menu_font)
        self.level_completed = False
        self.current_popup = None
        self.level_state = 1
        self.editing_loop = None
        self.editing_text = ""
        self.editing_loop_index = None
        self.bullet_surface = pygame.Surface((BULLET_RADIUS * 2, BULLET_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.bullet_surface, ORANGE, (BULLET_RADIUS, BULLET_RADIUS), BULLET_RADIUS)
        self.command_queue = []
        self.current_command = None
        self.command_start_time = 0
        self.command_delay = 50  # ms between commands
        self.player = Player(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size,
                             self.player_angle)
        self.alien = Alien()
        self.current_approaching_alien_bullet_shape = None  # Reset each frame
        self.current_approaching_alien_bullet_shape_temp = None
        # Common commands
        self.commands = {
            "move": {"color": (0, 100, 200), "text": "Move Forward"},
            "turn_left": {"color": (200, 100, 0), "text": "Turn Left"},
            "turn_right": {"color": (20, 100, 0), "text": "Turn Right"},
            "reverse": {"color": (250, 100, 0), "text": "Reverse"},
            "shoot": {"color": (250, 100, 0), "text": "Shoot"}
        }
        self._init_commands()
        self.var_dict = {
            "shape": "circle",
        }
        self.bullets_shape_match = {
            "circle": "square",
            "square": "triangle",
            "triangle": "circle"
        }

        self.op_dict = {
            ">": "Greater than",
            "<": "Less than",
            "==": "Equal to",
            ">=": "Greater or equal",
            "<=": "Less or equal",
            "!=": "Not equal"
        }

        self.commands_match = False
        self.level_id = 0
        self.exit_to_levels = False
        self.cmd_gen = None

    def reset_level(self, code_font, title_font, menu_font):
        self.__init__(code_font, title_font, menu_font)

        """self.bullet_options.append(
            Circle(val_box.centerx, val_box.centery, int(0.15 * (val_box.right - val_box.left)), WHITE))
        self.bullet_options.append(
            Square(val_box.centerx - 10, val_box.centery - 10, int(0.3 * (val_box.right - val_box.left)), WHITE))
        self.bullet_options.append(Triangle(
            [(val_box.bottomleft[0] + 15, val_box.bottomleft[1] - 5), (val_box.midtop[0], val_box.midtop[1] + 5),
             (val_box.bottomright[0] - 15, val_box.bottomright[1] - 5)], WHITE))"""

    def _init_commands(self):
        """Initialize the available command types"""
        basic_commands = list(self.commands.keys())
        for cmd_type in basic_commands:
            self.code_blocks.append(Command(cmd_type))

    def _check_bullet_bullet_collision(self, bullet1, bullet2):
        """Checks for AABB collision between two bullets."""
        # Assuming bullets are drawn from their center (x,y) and have a radius
        # For AABB, we can use their bounding boxes
        rect1 = pygame.Rect(bullet1.x - bullet1.radius, bullet1.y - bullet1.radius,
                            bullet1.radius * 2, bullet1.radius * 2)
        rect2 = pygame.Rect(bullet2.x - bullet2.radius, bullet2.y - bullet2.radius,
                            bullet2.radius * 2, bullet2.radius * 2)

        return rect1.colliderect(rect2)

    def update(self, dt):
        """Call this every frame from your main game loop"""
        self.player.update_bullets(self.alien, self.level_id, dt)
        if self.level_id == 3:
            self.alien.update_bullets(self.player, self.level_id, dt)
        #self.current_approaching_alien_bullet_shape = None  # Reset each frame
        closest_dist = float('inf')

        for bullet in self.alien.bullets:
            if bullet.active:
                # Calculate distance from bullet to player's center
                bullet_center_x = bullet.x
                bullet_center_y = bullet.y
                player_center_x = self.player.x + self.player.width // 2
                player_center_y = self.player.y + self.player.height // 2

                dist = math.sqrt((bullet_center_x - player_center_x) ** 2 + (bullet_center_y - player_center_y) ** 2)

                if dist < PLAYER_AWARENESS_RANGE and dist < closest_dist:
                    closest_dist = dist
                    self.current_approaching_alien_bullet_shape = bullet.shape
                    self.var_dict["shape"] = self.current_approaching_alien_bullet_shape

        player_bullets_after_b2b = []
        alien_bullets_after_b2b = []

        for p_bullet in self.player.bullets:
            if not p_bullet.active:
                self.player.bullet_pool.append(p_bullet)  # Recycle inactive player bullets
                continue

            hit_alien_bullet = False
            for a_bullet in self.alien.bullets:
                if not a_bullet.active:
                    # Already inactive, ensure it's in pool (should be handled by alien.update_bullets)
                    continue

                # Check for collision between player bullet and alien bullet
                if self._check_bullet_bullet_collision(p_bullet, a_bullet):
                    p_bullet.active = False  # Player bullet is destroyed
                    a_bullet.active = False  # Alien bullet is destroyed
                    self.player.bullet_pool.append(p_bullet)  # Recycle player bullet
                    self.alien.bullet_pool.append(a_bullet)  # Recycle alien bullet
                    if self.bullets_shape_match[a_bullet.shape] == p_bullet.shape:
                        self.alien.health= max(0, self.alien.health - DAMAGE_PER_HIT)  # Decrease player health
                    else:
                        self.player.health = max(0, self.player.health - DAMAGE_PER_HIT)
                    hit_alien_bullet = True  # Mark that this player bullet hit something
                    break  # This player bullet hit an alien bullet, no need to check other alien bullets

            if not hit_alien_bullet and p_bullet.active:  # If player bullet didn't hit an alien bullet and is still active
                player_bullets_after_b2b.append(p_bullet)

        # Now, update the actual lists, ensuring no duplicates or already inactive bullets are processed
        # This part needs to be careful to not re-add bullets that were just recycled.
        # The simplest way is to rebuild the lists from active bullets.
        self.player.bullets = [b for b in player_bullets_after_b2b if b.active]
        self.alien.bullets = [b for b in self.alien.bullets if b.active]  # Re-filter alien bullets too

        #self.update_commands(dt)

    def update_commands(self, dt):
        if not self.command_queue and not self.current_command:
            return

        current_time = pygame.time.get_ticks()

        # If no command is executing, start the next one
        if self.current_command is None:
            self.current_command = self.command_queue.pop(0)
            self.command_start_time = current_time
            self.execute_commands([self.current_command])  # Immediate first execution

        # Check if command duration has elapsed
        elif current_time - self.command_start_time >= self.command_delay:
            self.current_command = None

            # If queue is empty, check for level completion
            #if not self.command_queue:
            #self.check_level_completion()

    def draw_health_bar(self, surface):
        bar_width = self.target.width
        bar_height = 10
        bar_x = self.target.x
        bar_y = self.target.y - bar_height - 5

        # Background
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))

        # Health level
        health_width = (self.target_health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))

        # Border
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def draw_bullets(self, surface):
        if not self.player.bullets and not self.alien.bullets:
            return
        if self.player.bullets:
            for bullet in self.player.bullets:
                bullet.draw(screen)
        if self.alien.bullets and self.level_id == 3:
            for bullet in self.alien.bullets:
                bullet.draw(screen)

    def draw_player(self, surface):
        # Player body
        body_rect = pygame.Rect(*self.player_pos, self.player_size, self.player_size)
        pygame.draw.rect(surface, CYAN, body_rect)

        # Gun (rotated based on angle)
        gun_length = self.player_size * 1.5
        gun_center = (body_rect.centerx, body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.player_angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.player_angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    def draw_code_blocks(self, surface):
        # Draw command blocks area (palette)
        pygame.draw.rect(surface, DARK_GRAY, self.commands_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.commands_area, 2, border_radius=5)

        # Draw available command palette
        for i, cmd in enumerate(self.code_blocks):
            cmd.rect = pygame.Rect(60 + i * 90, 15, 90, 25)
            pygame.draw.rect(surface, cmd.color, cmd.rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, cmd.rect, 2, border_radius=3)
            text = self.code_font.render(cmd.text, True, WHITE)
            surface.blit(text, (cmd.rect.x + 5, cmd.rect.y + 5))

        # Draw main code area background
        pygame.draw.rect(surface, DARK_GRAY, self.code_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.code_area, 2, border_radius=5)

        # Draw all commands recursively
        #y_offset = self.code_area.y + 10
        for cmd in self.main_code:
            prev_cmd = self.main_code[self.main_code.index(cmd) - 1]
            if prev_cmd.is_loop() and self.main_code.index(cmd) - 1 >= 0:
                cmd.rect.y = prev_cmd.rect.y + prev_cmd.rect.height
            cmd_height = cmd.draw(
                surface,
                cmd.rect.x,
                cmd.rect.y,
                self.code_area.width - 20
            )
            #y_offset += cmd_height + 5

    def _cycle_value(self, current, options_dict):
        """Cycle to next value in dictionary"""
        if not options_dict:
            return ""

        options = list(options_dict.keys())
        if current not in options:
            return options[0]

        current_index = options.index(current)
        next_index = (current_index + 1) % len(options)
        return options[next_index]

    def _get_condition_boxes(self, cmd):
        """Get the rects for condition boxes"""
        if_text = self.code_font.render("if", True, WHITE)
        box_start_x = cmd.rect.x + 10 + if_text.get_width() + 10
        box_width = 60
        op_width = 30
        box_height = 20
        box_y = cmd.rect.y + 5

        var_box = pygame.Rect(box_start_x, box_y, box_width, box_height)
        op_box = pygame.Rect(box_start_x + box_width + 5, box_y, op_width, box_height)
        val_box = pygame.Rect(box_start_x + box_width + op_width + 10, box_y, box_width, box_height)

        return var_box, op_box, val_box

    def handle_events(self, event, mouse_pos):
        global main_code_height
        # Handle mouse button down events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on command palette
            for block in self.code_blocks:
                if block.rect.collidepoint(mouse_pos):
                    self.dragging = {
                        "type": block.cmd_type,
                        "offset": (mouse_pos[0] - block.rect.x,
                                   mouse_pos[1] - block.rect.y)
                    }
                    return

            # Check if clicking on loop iteration box
            for i, cmd in enumerate(self.main_code):
                if cmd.is_loop():
                    iteration_box = self._get_iteration_box(cmd)
                    if iteration_box.collidepoint(mouse_pos):
                        self.editing_loop_index = i
                        self.editing_text = ""
                        return
                if cmd.is_conditional() or cmd.cmd_type == "while_loop":
                    var_box, op_box, val_box = self._get_condition_boxes(cmd)

                    if var_box.collidepoint(mouse_pos):
                        # Cycle through variables
                        current_var = getattr(cmd, 'condition_var', None)
                        cmd.condition_var = self._cycle_value(current_var, self.var_dict)
                        cmd.editing_condition_part = None  # Not typing, just cycling

                    elif op_box.collidepoint(mouse_pos):
                        # Cycle through operators
                        current_op = getattr(cmd, 'condition_op', None)
                        cmd.condition_op = self._cycle_value(current_op, self.op_dict)
                        cmd.editing_condition_part = None  # Not typing, just cycling

                    elif val_box.collidepoint(mouse_pos):
                        # Start typing for value
                        cmd.editing_condition_part = 'val'

                        if not hasattr(cmd, 'condition_val'):
                            cmd.condition_val = ""

            # Clear editing state if clicked elsewhere
            self.editing_loop_index = None

        # Handle mouse button up (dropping commands)
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            if self.code_area.collidepoint(mouse_pos):
                # Check if dropping onto an existing loop block
                for cmd in self.main_code:
                    if (cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop") and cmd.rect.collidepoint(mouse_pos):
                        #rel_y = mouse_pos[1] - cmd.rect.y

                        # Only add if dropped in the body area (below header)
                        if True:
                            #nested_index = (rel_y - 40) // 25
                            #nested_index = max(0, min(nested_index, len(cmd.nested_commands)))

                            #for a in range(nested_index+1, len(cmd.nested_commands)):
                            #cmd.nested_commands[a].rect.y += 25

                            # Create new command of the dragged type
                            new_cmd = Command(
                                cmd_type=self.dragging["type"],
                                iterations=3 if self.dragging["type"] == "for_loop" else 1,
                                nested_commands=[] if self.dragging[
                                                          "type"] == "for_loop" or "if_statement" or "while_loop" else None,
                                rect=pygame.Rect(
                                    cmd.rect.x + 20,
                                    cmd.rect.height + cmd.rect.y,
                                    160 if self.dragging[
                                               "type"] != "for_loop" or "if_statement" or "while_loop" else 190,
                                    25 if self.dragging[
                                              "type"] != "for_loop" or "if_statement" or "while_loop" else 40,
                                ),
                                code_font=self.code_font
                            )

                            cmd.nested_commands.append(new_cmd)
                            self.dragging = None
                            #self.recalculate_code_positions()
                            return

                # If not dropped on a loop, add to main code
                self.add_to_main_code(self.dragging["type"], mouse_pos)

            self.dragging = None
            #self.recalculate_code_positions()


        elif event.type == pygame.KEYDOWN:

            # Only allow typing for value box

            for cmd in self.main_code:

                if hasattr(cmd, 'editing_condition_part') and cmd.editing_condition_part == 'val':

                    if event.key == pygame.K_RETURN:

                        cmd.editing_condition_part = None

                    elif event.key == pygame.K_BACKSPACE:

                        cmd.condition_val = cmd.condition_val[:-1]

                    elif event.unicode.isdigit():  # Only allow numbers for values

                        cmd.condition_val += event.unicode

                if self.editing_loop_index is not None:
                    #cmd = self.main_code[self.editing_loop_index]

                    if event.key == pygame.K_RETURN:
                        if self.editing_text.isdigit() and int(self.editing_text) > 0:
                            cmd.iterations = min(99, int(self.editing_text))
                        self.editing_loop_index = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.editing_text = self.editing_text[:-1]
                    elif event.unicode.isdigit():
                        if len(self.editing_text) < 2:
                            self.editing_text += event.unicode
                        else:
                            self.editing_text = ""

        # Handle iteration count editing
        """elif event.type == pygame.KEYDOWN and self.editing_loop_index is not None:
            cmd = self.main_code[self.editing_loop_index]

            if event.key == pygame.K_RETURN:
                if self.editing_text.isdigit() and int(self.editing_text) > 0:
                    cmd.iterations = min(99, int(self.editing_text))
                self.editing_loop_index = None
            elif event.key == pygame.K_BACKSPACE:
                self.editing_text = self.editing_text[:-1]
            elif event.unicode.isdigit():
                if len(self.editing_text) < 2:
                    self.editing_text += event.unicode"""

        # Handle run button
        if self.run_button.is_clicked(mouse_pos, event):
            """if not self.command_queue:
                self.command_queue = self.main_code.copy()
            self.current_command = None"""
            self.cmd_gen = self.execute_commands(self.main_code)

            #self.execute_commands(self.main_code, screen, mouse_pos, event)

        # Handle reset button
        if self.reset_button.is_clicked(mouse_pos, event):
            self.main_code = []
            main_code_height = 0
            #self.recalculate_code_positions()

    def _get_iteration_box(self, cmd):
        """Get the rect for the iteration input box of a loop command"""
        header_text = "Repeat "
        text_width = self.code_font.size(header_text)[0]
        return pygame.Rect(
            cmd.rect.x + 10 + text_width,
            cmd.rect.y + 5,
            60,
            20
        )

    def execute_commands(self, cmd_list):
        step_delay = 0
        for cmd in cmd_list:
            #print(cmd.cmd_type)
            if cmd.is_loop():
                for _ in range(cmd.iterations):
                    #self.command_queue[:0] = cmd.nested_commands
                    #self.update_commands(dt)
                    yield from self.execute_commands(cmd.nested_commands)
            elif cmd.is_conditional():
                if self.var_dict[cmd.condition_var] == cmd.condition_val.shape:
                    #self.command_queue[:0] = cmd.nested_commands
                    #self.update_commands(dt)
                    yield from self.execute_commands(cmd.nested_commands)
            elif cmd.cmd_type == "while_loop":
                while True:
                    yield from self.execute_commands(cmd.nested_commands)
                #self.execute_commands(cmd.nested_commands)




            else:
                if cmd.cmd_type == "move":
                    dx = 50 * math.sin(math.radians(self.player.angle))
                    dy = -50 * math.cos(math.radians(self.player.angle))
                    self.player.x += dx
                    self.player.y += dy

                    # Boundary checking
                    self.player.x = max(self.battlefield.left,
                                        min(self.player.x, self.battlefield.right - self.player.width))
                    self.player.y = max(self.battlefield.top,
                                        min(self.player.y, self.battlefield.bottom - self.player.height))
                elif cmd.cmd_type == "turn_left":
                    self.player.angle = (self.player.angle - 90) % 360

                elif cmd.cmd_type == "reverse":
                    dx = 20 * math.sin(math.radians(self.player.angle))
                    dy = -20 * math.cos(math.radians(self.player.angle))
                    self.player.x -= dx
                    self.player.y -= dy

                    # Boundary checking
                    self.player.x = max(self.battlefield.left,
                                        min(self.player.x, self.battlefield.right - self.player.width))
                    self.player.y = max(self.battlefield.top,
                                        min(self.player.y, self.battlefield.bottom - self.player.height))

                elif cmd.cmd_type == "turn_right":
                    self.player.angle = (self.player.angle + 90) % 360

                elif cmd.cmd_type == "shoot":
                    #if self.current_approaching_alien_bullet_shape != self.current_approaching_alien_bullet_shape_temp:
                    shape = cmd.shoot_target_shape.shape
                    self.player.shoot_bullet(shape=shape)
                    #self.current_approaching_alien_bullet_shape_temp = self.current_approaching_alien_bullet_shape

                yield

            #pygame.time.wait(step_delay)
                #screen.fill(BLACK)
            #self.draw_all(screen, mouse_pos, event)
            #pygame.display.update()

    def add_to_main_code(self, command_type, mouse_pos):
        """Add a command or loop block to main code"""
        # Calculate position in code area
        pos_in_area = (mouse_pos[0] - self.code_area.x, mouse_pos[1] - self.code_area.y)

        insert_index = len(self.main_code)
        for i, cmd in enumerate(self.main_code):
            if mouse_pos[1] < cmd.rect.centery:
                insert_index = i
                break

        # Calculate y-position for the new command
        if insert_index > 0:
            # Position after the previous command
            prev_cmd = self.main_code[insert_index - 1]
            for a in range(insert_index, len(self.main_code)):
                self.main_code[a].rect.y += 40
            y_pos = prev_cmd.rect.bottom + 10
        else:
            # First command in the list
            y_pos = self.code_area.y + 10

        if command_type == "for_loop":
            new_cmd = Command(
                cmd_type="for_loop",
                iterations=3,
                nested_commands=[],
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    60  # Initial height
                ),
                code_font=self.code_font
            )
        elif command_type == "if_statement":
            new_cmd = Command(
                cmd_type= "if_statement",
                iterations=1,
                nested_commands=[],
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    60
                ),
                conditions={},
                code_font=self.code_font
            )

        elif command_type == "while_loop":
            new_cmd = Command(
                cmd_type= "while_loop",
                iterations=1,
                nested_commands=[],
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    60
                ),
                conditions={},
                code_font=self.code_font
            )

        else:
            new_cmd = Command(
                cmd_type=command_type,
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    25 # Initial height
                ),
                code_font=self.code_font
            )

        # Insert at the correct position
        self.main_code.insert(insert_index, new_cmd)
        #self.recalculate_code_positions()

    def draw_popups(self, screen, mouse_pos, event):
        """To be implemented by subclasses"""
        if self.alien.health <= 0:
            popup_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 300, 150)
            pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=10)
            pygame.draw.rect(screen, GREEN, popup_rect, 2, border_radius=10)

            text = self.title_font.render("Good Job!", True, GREEN)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 20))

            continue_btn = Button(popup_rect.centerx - 75, popup_rect.top + 80, 150, 40,
                                  "Continue", BLUE, CYAN, self.menu_font)
            continue_btn.draw(screen)
            if continue_btn.is_clicked(mouse_pos, event):
                self.current_popup = None
                self.exit_to_levels = True
                """self.commands.update({
                    "turn_right": {"color": (20, 100, 0), "text": "Turn Right"},
                    "reverse": {"color": (250, 100, 0), "text": "Reverse"}
                })"""
        if self.player.health <= 0:
            popup_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 300, 150)
            pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=10)
            pygame.draw.rect(screen, GREEN, popup_rect, 2, border_radius=10)

            text = self.title_font.render("The aliens killed you!", True, GREEN)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 20))

            continue_btn = Button(popup_rect.centerx - 75, popup_rect.top + 80, 150, 40,
                                  "Continue", BLUE, CYAN, self.menu_font)
            continue_btn.draw(screen)
            if continue_btn.is_clicked(mouse_pos, event):
                self.current_popup = None
                self.exit_to_levels = True

    def draw_all(self, screen, mouse_pos, event):
        # Common drawing code
        pygame.draw.rect(screen, GRAY, self.battlefield, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.battlefield, 2, border_radius=5)
        #pygame.draw.rect(screen, RED, self.target, border_radius=3)
        self.alien.draw_player(screen)
        self.player.draw_player(screen)
        self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.alien.draw_health_bar(screen)
        if self.level_id == 3:
            self.player.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_popups(screen, mouse_pos, event)  # Delegate popups to subclasses

    def draw_game(self, screen, mouse_pos, event):
        self.alien.draw_player(screen)
        self.player.draw_player(screen)
        #self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.alien.draw_health_bar(screen)
        if self.level_id == 3:
            self.player.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_popups(screen, mouse_pos, event)


# --- Level Specific Implementations ---
