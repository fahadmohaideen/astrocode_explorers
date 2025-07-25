import pygame
import math
import collections
import copy
import random
import os

from core.constants import (
    WIDTH, HEIGHT, BLACK, WHITE, GRAY, BLUE, DARK_GRAY, RED, GREEN, CYAN, ORANGE,
    FOR_LOOP_COLOR, BULLET_RADIUS, TARGET_MAX_HEALTH, PLAYER_MAX_HEALTH,
    DAMAGE_PER_HIT, PLAYER_AWARENESS_RANGE, COMMAND_DELAY_MS, screen, ORIGINAL_CMD_WIDTH, ORIGINAL_CMD_HEIGHT_LOOP, ALIEN_TYPES, DARK_OVERLAY_COLOR
)
#from game1 import code_font
from ui.button import Button
from entities.player import Player
from entities.alien import Alien
from entities.bullet import Bullet
from entities.commands import Command


from core.constants import CODE_FONT_SIZE

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
        self.player_size = 50
        self.player_pos = [
            self.battlefield.centerx + 250,
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
        #self.code_area = pygame.Rect(500, 100, 250, 400)
        self.code_area = pygame.Rect(300, 10, 500, 700)
        #self.commands_area = pygame.Rect(50, 5, 700, 50)
        self.commands_area = pygame.Rect(10, 10, 250, 700)
        self.run_button = Button(625, 725, 100, 40, "Run", GREEN, (0, 200, 0), self.menu_font)
        self.reset_button = Button(375, 725, 100, 40, "Reset", RED, (200, 0, 0), self.menu_font)
        button_size = 30
        margin = 10
        self.exit_button_rect = pygame.Rect(
            self.code_area.right - button_size - margin,  # X position
            self.code_area.top + margin,  # Y position
            button_size,  # Width
            button_size  # Height
        )
        self.level_completed = False
        self.current_popup = None
        self.level_state = 1
        self.editing_loop = None
        self.editing_text = ""
        self.editing_loop_cmd = None
        self.bullet_surface = pygame.Surface((BULLET_RADIUS * 2, BULLET_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.bullet_surface, ORANGE, (BULLET_RADIUS, BULLET_RADIUS), BULLET_RADIUS)
        self.command_queue = []
        self.current_command = None
        self.command_start_time = 0
        self.command_delay = 50  # ms between commands
        self.player = Player(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size,
                             self.player_angle)
        self.player.speed = 300
        self.aliens = []
        self.current_approaching_alien_bullet_shape = None  # Reset each frame
        self.current_approaching_alien_bullet_shape_temp = None
        # Common commands
        self.commands = {
            "move_up": {"color": (0, 100, 200), "text": "Move Up"},
            "move_left": {"color": (200, 100, 0), "text": "Move Left"},
            "move_right": {"color": (20, 100, 0), "text": "Move Right"},
            "move_down": {"color": (250, 100, 0), "text": "Move_down"},
            "shoot": {"color": (250, 100, 0), "text": "Shoot"}
        }
        self._init_commands()
        self.var_dict = {

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
        self.cmd_tree = None
        self.code_editor = False
        self.game_view = True
        self.camera_active = True
        self.camera_offset = pygame.Vector2(0, 0)
        self.enable_wasd = False
        self.curr_nearest_alien = None
        self.moving = False
        self.TILE_SIZE = 50
        self.PANEL_COLOR = (30, 30, 30, 200)
        self.frame_index = 0
        self.animation_counter = 0
        self.animation_speed = 0.2
        self.aliens_eliminated = 0
        self.total_aliens_to_eliminate = 3
        #self.spawn_aliens(3)

    def reset_level(self, code_font, title_font, menu_font):
        self.__init__(code_font, title_font, menu_font)

    def _init_commands(self):
        """Initialize the available command types"""
        basic_commands = list(self.commands.keys())
        for cmd_type in basic_commands:
            self.code_blocks.append(Command(cmd_type))

    def update_camera(self):
        """Update camera position to follow hero"""
        if self.camera_active:
            self.camera_offset.x = self.player.pos.x - self.player_pos[0]
            self.camera_offset.y = self.player.pos.y - self.player_pos[1]

    def load_assets(self):
        ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

        # Load tile and hero images
        raw_tile = pygame.image.load(os.path.join(ASSETS_PATH, "tile.png"))
        self.tile_img = pygame.transform.scale(raw_tile, (self.TILE_SIZE, self.TILE_SIZE))
        self.hero_img = pygame.image.load(os.path.join(ASSETS_PATH, "hero.png"))
        self.hero_img = pygame.transform.scale(self.hero_img, (55, 55))
        self.hero_rect = self.hero_img.get_rect(
            center=(self.battlefield.centerx,
                    self.battlefield.bottom - self.player_size // 2 - 5)
        )
        self.player.pos = pygame.Vector2(self.hero_rect.x, self.hero_rect.y)

        # Load animation frames
        self.walk_frames = [
            pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "walk1.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "walk2.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "walk3.png")), (50, 50))
        ]

        for alien in ALIEN_TYPES.keys():
            img = pygame.image.load(os.path.join(ASSETS_PATH, f"{'_'.join(alien.split())}.png"))
            self.var_dict[alien][2] = pygame.transform.scale(img, (60, 60))

    def spawn_aliens(self, count):
        """Spawn aliens at random positions with better distribution"""
        spawn_margin = 300  # Minimum distance from screen edges
        spawn_area_width = WIDTH + 1000
        spawn_area_height = HEIGHT + 1000
        quad_nums = [a for a in range(count)]

        for b in range(count):
            alien_type = list(ALIEN_TYPES.keys())[b]
            # Spawn in one of four quadrants around the player
            quadrant = random.choice(quad_nums)
            if quadrant == 0:  # Top-right
                x = random.randint(WIDTH // 2 + 200, spawn_area_width)
                y = random.randint(0, HEIGHT // 2 - 200)
                quad_nums.remove(quadrant)
            elif quadrant == 1:  # Bottom-right
                x = random.randint(WIDTH // 2 + 200, spawn_area_width)
                y = random.randint(HEIGHT // 2 + 200, spawn_area_height)
                quad_nums.remove(quadrant)
            elif quadrant == 2:  # Top-left
                x = random.randint(0, WIDTH // 2 - 200)
                y = random.randint(0, HEIGHT // 2 - 200)
                quad_nums.remove(quadrant)
            else:  # Bottom-left
                x = random.randint(0, WIDTH // 2 - 200)
                y = random.randint(HEIGHT // 2 + 200, spawn_area_height)
                quad_nums.remove(quadrant)


            self.aliens.append(Alien(x, y, alien_type))

    def draw_minimap(self):
        map_size = 150
        map_pos = (WIDTH - map_size - 10, 10)
        pygame.draw.rect(screen, (50, 50, 50), (*map_pos, map_size, map_size))

        # Draw hero on minimap
        hero_map_x = map_pos[0] + (self.player.pos.x / (WIDTH + 1000)) * map_size
        hero_map_y = map_pos[1] + (self.player.pos.y / (HEIGHT + 1000)) * map_size
        pygame.draw.circle(screen, (0, 255, 0), (int(hero_map_x), int(hero_map_y)), 5)

        # Draw aliens on minimap
        for alien in self.aliens:
            alien_map_x = map_pos[0] + (alien.pos.x / (WIDTH + 1000)) * map_size
            alien_map_y = map_pos[1] + (alien.pos.y / (HEIGHT + 1000)) * map_size
            dot_color = ALIEN_TYPES[alien.name]

            if self.level_id == 2:
                dot_color = GREEN
            pygame.draw.circle(screen, dot_color,
                               (int(alien_map_x), int(alien_map_y)), 3)

    def draw_alien_dir(self):
        for alien in self.aliens:
            alien_screen_pos = alien.pos - self.camera_offset

            # Draw direction indicator if off-screen
            if not (-100 < alien_screen_pos.x < WIDTH + 100 and
                    -100 < alien_screen_pos.y < HEIGHT + 100):
                # Calculate direction to alien
                dir_vec = (alien.pos - self.player.pos).normalize()
                indicator_pos = self.player.offset_pos + dir_vec * 200
                indicator_color = ALIEN_TYPES[alien.name]

                if self.level_id == 2:
                    indicator_color = WHITE

                # Draw arrow pointing to alien
                pygame.draw.circle(screen, indicator_color,
                                   (int(indicator_pos.x), int(indicator_pos.y)), 10)
                pygame.draw.line(screen, indicator_color,
                                 (self.player.offset_pos.x, self.player.offset_pos.y),
                                 (indicator_pos.x, indicator_pos.y), 2)
                continue

    def _check_bullet_bullet_collision(self, bullet1, bullet2):
        """Checks for AABB collision between two bullets."""
        # Assuming bullets are drawn from their center (x,y) and have a radius
        # For AABB, we can use their bounding boxes
        rect1 = pygame.Rect(bullet1.x - bullet1.radius, bullet1.y - bullet1.radius,
                            bullet1.radius * 2, bullet1.radius * 2)
        rect2 = pygame.Rect(bullet2.x - bullet2.radius, bullet2.y - bullet2.radius,
                            bullet2.radius * 2, bullet2.radius * 2)

        return rect1.colliderect(rect2)

    def draw_terrain(self, surface):
        """Draw tiled background with camera offset"""
        for x in range(-self.TILE_SIZE, WIDTH + self.TILE_SIZE, self.TILE_SIZE):
            for y in range(-self.TILE_SIZE, HEIGHT + self.TILE_SIZE, self.TILE_SIZE):
                surface.blit(self.tile_img,
                             (x - self.camera_offset.x % self.TILE_SIZE,
                              y - self.camera_offset.y % self.TILE_SIZE))


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
        for bullet in self.player.bullets:
            bullet.draw(surface, self.camera_offset)
        for alien in self.aliens:
            for bullet in alien.bullets:
                bullet.draw(surface, self.camera_offset)
        """if self.alien.bullets:
            for bullet in self.alien.bullets:
                bullet.draw(screen)"""

    def draw_player(self, surface):
        # Player body
        body_rect = self.hero_img.get_rect(
            center=(self.battlefield.centerx - self.camera_offset.x,
                    self.battlefield.bottom - self.player_size // 2 - 5 - self.camera_offset.y)
        )
        screen.blit(self.walk_frames[frame_index], body_rect)
        pygame.draw.rect(surface, CYAN, body_rect)

        # Gun (rotated based on angle)
        gun_length = self.player_size * 1.5
        gun_center = (body_rect.centerx, body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.player_angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.player_angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    def check_alignment(self, cmd_list):
        if not cmd_list:
            return
        for a in range(len(cmd_list)):
            if a > 0:
                cmd_list[a].rect.y = cmd_list[a-1].rect.height + cmd_list[a-1].rect.y
            if cmd_list[a].is_loop():
                self.check_alignment(cmd_list[a].nested_commands)

    def draw_code_blocks(self, surface):
        # Draw command blocks area (palette)
        pygame.draw.rect(surface, DARK_GRAY, self.commands_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.commands_area, 2, border_radius=5)

        # Draw available command palette
        for i, cmd in enumerate(self.code_blocks):
            cmd.rect = pygame.Rect(40, 20 + i*75 , 150, 50)
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
            cmd_height = cmd.draw(
                surface,
                cmd.rect.x,
                cmd.rect.y,
                self.code_area.width - 20
            )
        self.check_alignment(self.main_code)
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

    def traverse_cmd(self, cmd_list, i):
        for cmd in cmd_list:
            if cmd.nested_commands:
                yield from self.traverse_cmd(cmd.nested_commands, i+1)
            else:
                yield cmd, i

    def print_cmd(self, cmd_list, i):
        for cmd in cmd_list:
            if cmd.nested_commands:
                self.traverse_cmd(cmd.nested_commands, i+1)
            else:
                print(cmd.cmd_type, i)

    def add_command(self, curr_cmd, i):
        new_cmd = Command(
            cmd_type=self.dragging["type"],
            iterations=3 if self.dragging["type"] == "for_loop" else 1,
            nested_commands=[] if self.dragging["type"] in ["for_loop", "if_statement",
                                                            "while_loop"] else None,
            rect=pygame.Rect(
                curr_cmd.rect.x + 10 * i,
                curr_cmd.rect.height + curr_cmd.rect.y,
                ORIGINAL_CMD_WIDTH - 20 * i,
                ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),
            ),
            depth=cmd.depth + 1,
            code_font=self.code_font
        )
        # print(new_cmd.cmd_type)
        curr_cmd.nested_commands.append(new_cmd)
        # print(i)
        self.dragging = None

    def handle_cmd_drop(self, cmd_list, mouse_pos, x, parent_cmd):
        for cmd in cmd_list:
            if cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop":
                if cmd.rect.collidepoint(mouse_pos):
                    self.handle_cmd_drop(cmd.nested_commands, mouse_pos, x+1, cmd)
                    return
        print(x)
        if x > 0:
            self.add_to_main_code(cmd_list, parent_cmd.rect, self.dragging, mouse_pos, x, parent_cmd)
        else:
            self.add_to_main_code(self.main_code, self.code_area, self.dragging, mouse_pos, 0, None)
        return

    def handle_events(self, event, mouse_pos):
        """Handles all user input, including clicks on command blocks and UI elements."""

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.code_editor and self.exit_button_rect.collidepoint(mouse_pos):
                self.code_editor = False
                self.game_view = True
                print("Command panel closed.")
                return
            if self.handle_command_clicks(self.main_code, mouse_pos):
                return


            for block in self.code_blocks:
                if block.rect and block.rect.collidepoint(mouse_pos):
                    self.dragging = {
                        "type": block.cmd_type,
                        "offset": (mouse_pos[0] - block.rect.x, mouse_pos[1] - block.rect.y)
                    }
                    return


            if self.player.body_rect.collidepoint(mouse_pos):
                self.code_editor = True
                self.game_view = False


        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            if self.code_area.collidepoint(mouse_pos):
                # Drop the dragged command into the code area.
                self.handle_cmd_drop(self.main_code, mouse_pos, 0, None)
            self.dragging = None

        elif event.type == pygame.KEYDOWN:
            if self.editing_loop_cmd is not None:
                cmd = self.editing_loop_cmd
                if event.key == pygame.K_RETURN:
                    if cmd.editing_text.isdigit() and int(cmd.editing_text) > 0:
                        cmd.iterations = min(99, int(cmd.editing_text))
                    self.editing_loop_cmd = None
                elif event.key == pygame.K_BACKSPACE:
                    cmd.editing_text = cmd.editing_text[:-1]
                elif event.unicode.isdigit() and len(cmd.editing_text) < 2:
                    cmd.editing_text += event.unicode
                else:
                    cmd.editing_text = ""  # Clear if invalid input

        if self.run_button.is_clicked(mouse_pos, event):
            print("=== RUN BUTTON CLICKED ===")
            self.code_editor = False
            self.game_view = True
            self.cmd_gen = self.execute_commands(self.main_code, None)  # Create the command generator.
            self._update_nearest_alien()
            print(f"Ready to execute with target: {self.curr_nearest_alien}")


        if self.reset_button.is_clicked(mouse_pos, event):
            self.main_code = []

    def execute_commands(self, cmd_list, parent_cmd):
        for cmd in cmd_list:
            if cmd.is_loop():
                for _ in range(cmd.iterations):
                    yield from self.execute_commands(cmd.nested_commands, cmd)
            elif cmd.is_conditional():
                if self.var_dict[cmd.condition_var][0]:
                    yield from self.execute_commands(cmd.nested_commands, cmd)
            elif cmd.cmd_type == "while_loop":
                while True:
                    yield from self.execute_commands(cmd.nested_commands, cmd)
            else:
                if cmd.cmd_type == "move_up":
                    dx = 50 * math.sin(math.radians(self.player.angle))
                    dy = -50 * math.cos(math.radians(self.player.angle))
                    self.player.pos += pygame.Vector2(dx, dy)
                elif cmd.cmd_type == "move_left":
                    self.player.pos -= pygame.Vector2(80, 0)
                elif cmd.cmd_type == "move_down":
                    self.player.pos += pygame.Vector2(0, 80)
                elif cmd.cmd_type == "move_right":
                    self.player.pos += pygame.Vector2(80, 0)
                elif cmd.cmd_type == "shoot":
                    direction = None


                    if self.level_id == 1:

                        direction = pygame.Vector2(1, 0)
                        print("Level 1: Firing straight right.")


                    else:
                        self._update_nearest_alien()
                        print(f"Attempting to shoot. Current target: {self.curr_nearest_alien}")
                        if self.curr_nearest_alien and self.curr_nearest_alien.active and self.curr_nearest_alien.health > 0:
                            direction = (self.curr_nearest_alien.pos - self.player.pos).normalize()
                        else:
                            print("No valid target to shoot at - target is dead or inactive")


                    if direction:
                        bullet_type = cmd.shoot_bullet_type if hasattr(cmd, 'shoot_bullet_type') else "Player"
                        color = ALIEN_TYPES.get(bullet_type, ORANGE)


                        bullet = self.player.shoot_bullet(
                            bullet_type=bullet_type,
                            direction=direction,
                            color=color
                        )
                        print(f"Bullet created at {bullet.pos} with direction {direction}")


                        for _ in range(3):
                            yield




    def _update_nearest_alien(self):
        """Updates the nearest active alien to target using world coordinates"""
        self.curr_nearest_alien = None
        min_dist = float('inf')

        # Filter for truly active aliens (alive and active)
        active_aliens = [a for a in self.aliens if a.active and a.health > 0]
        if not active_aliens:
            print("No active aliens remaining")
            return

        for alien in active_aliens:
            # Use world-space distance for consistent targeting
            dist = (alien.pos - self.player.pos).length()

            if dist < min_dist:
                min_dist = dist
                self.curr_nearest_alien = alien

        # Debug output
        if self.curr_nearest_alien:
            print(f"Targeting {self.curr_nearest_alien.name} at distance {min_dist:.2f}")
        else:
            print("No valid targets found")

        # In levels/base_level.py, inside the Level class

    def handle_command_clicks(self, cmd_list, mouse_pos):
        """Recursively checks for clicks on special command UI elements."""
        for cmd in cmd_list:
            # Check if the user clicked on the bullet type selector
            if cmd.cmd_type == "shoot" and cmd.shoot_type_rect and cmd.shoot_type_rect.collidepoint(mouse_pos):

                current_index = cmd.bullet_types.index(cmd.shoot_bullet_type)
                next_index = (current_index + 1) % len(cmd.bullet_types)
                cmd.shoot_bullet_type = cmd.bullet_types[next_index]
                return True


            if cmd.nested_commands:
                if self.handle_command_clicks(cmd.nested_commands, mouse_pos):
                    return True
        return False


    def add_to_main_code(self, cmd_list, cmd_rect, command_type, mouse_pos, i, parent_cmd):
        """Add a command or loop block to main code"""
        # Calculate position in code area
        pos_in_area = (mouse_pos[0] - self.code_area.x, mouse_pos[1] - self.code_area.y)

        insert_index = len(cmd_list)
        for b, cmd in enumerate(cmd_list):
            if mouse_pos[1] < cmd.rect.centery:
                insert_index = b
                break

        # Calculate y-position for the new command
        if insert_index > 0:
            # Position after the previous command
            prev_cmd = cmd_list[insert_index - 1]
            for a in range(insert_index, len(cmd_list)):
                cmd_list[a].rect.y = cmd_list[a-1].rect.height + cmd_list[a-1].rect.y
            y_pos = prev_cmd.rect.bottom
        else:
            # First command in the list
            y_pos = cmd_rect.y + 20

        if command_type == "for_loop":
            new_cmd = Command(
                cmd_type="for_loop",
                iterations=3,
                nested_commands=[],
                rect=pygame.Rect(
                    parent_cmd.rect.x + 10  if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),# Initial height
                ),
                depth= 0 if not parent_cmd else parent_cmd.depth + 1,
                code_font=self.code_font,
                original_rect = pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),# Initial height
                )
            )
        elif command_type == "if_statement":
            new_cmd = Command(
                cmd_type= "if_statement",
                iterations=1,
                nested_commands=[],
                rect=pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),  # Initial height
                ),
                conditions={},
                depth=0 if not parent_cmd else parent_cmd.depth + 1,
                code_font=self.code_font,
                original_rect = pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),  # Initial height
                )
            )

        elif command_type == "while_loop":
            new_cmd = Command(
                cmd_type= "while_loop",
                iterations=1,
                nested_commands=[],
                rect=pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i ,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),  # Initial height
                ),
                conditions={},
                depth=0 if not parent_cmd else parent_cmd.depth + 1,
                code_font=self.code_font,
                original_rect = pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20 * i,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),  # Initial height
                )
            )

        else:
            new_cmd = Command(
                cmd_type=command_type["type"],
                rect=pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i ,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),
                    # Initial height  # Initial height # Initial height
                ),
                depth=0 if not parent_cmd else parent_cmd.depth + 1,
                code_font=self.code_font,
                original_rect = pygame.Rect(
                    parent_cmd.rect.x + 10 if parent_cmd else self.code_area.x + 20,
                    y_pos,
                    ORIGINAL_CMD_WIDTH - 20*i ,
                    ORIGINAL_CMD_HEIGHT_LOOP * math.pow(0.5, i),
                    # Initial height  # Initial height # Initial height
                )
            )

        # Insert at the correct position
        #new_cmd.original_rect = new_cmd.rect
        cmd_list.insert(insert_index, new_cmd)
        #self.recalculate_code_positions()

    def update_aliens(self):
        """Update alien states including disappearance effects"""
        aliens_to_remove = []
        elimination_count = 0

        for alien in self.aliens:
            if alien.health <= 0 and not alien.disappearing:
                # Start disappearance effect
                alien.disappearing = True
                alien.disappear_timer = alien.disappear_duration

            if alien.disappearing:
                alien.disappear_timer -= 1
                if alien.disappear_timer <= 0:
                    aliens_to_remove.append(alien)
                    elimination_count += 1

        # Remove dead aliens
        for alien in aliens_to_remove:
            self.aliens.remove(alien)

        return elimination_count

    def spawn_aliens_with_types(self, alien_types):
        """Spawns aliens of specific types provided in a list."""
        count = len(alien_types)
        spawn_margin = 300
        spawn_area_width = WIDTH + 1000
        spawn_area_height = HEIGHT + 1000
        quad_nums = list(range(count))

        for i in range(count):
            alien_type = alien_types[i]
            quadrant = random.choice(quad_nums)
            if quadrant == 0:  # Top-right
                x = random.randint(WIDTH // 2 + 200, spawn_area_width)
                y = random.randint(0, HEIGHT // 2 - 200)
            elif quadrant == 1:  # Bottom-right
                x = random.randint(WIDTH // 2 + 200, spawn_area_width)
                y = random.randint(HEIGHT // 2 + 200, spawn_area_height)
            elif quadrant == 2:  # Top-left
                x = random.randint(0, WIDTH // 2 - 200)
                y = random.randint(0, HEIGHT // 2 - 200)
            else:  # Bottom-left
                x = random.randint(0, WIDTH // 2 - 200)
                y = random.randint(HEIGHT // 2 + 200, spawn_area_height)

            if quad_nums:
                quad_nums.remove(quadrant)

            self.aliens.append(Alien(x, y, alien_type))

    def draw_disappearing_aliens(self, surface):
        """Draw aliens with disappearance effects"""
        for alien in self.aliens:
            if alien.disappearing:
                # Calculate alpha based on disappear timer
                alpha = int(255 * (alien.disappear_timer / alien.disappear_duration))

                # Create a copy of the image with alpha applied
                alien_img_copy = self.var_dict[alien.name][2].copy()
                alien_img_copy.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)

                # Draw with shrinking effect
                scale = 1.0 - (1.0 - (alien.disappear_timer / alien.disappear_duration)) * 0.5
                scaled_img = pygame.transform.scale(
                    alien_img_copy,
                    (int(60 * scale), int(60 * scale))
                )

                # Draw with pulsing effect
                pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5 * (
                            1 - (alien.disappear_timer / alien.disappear_duration))
                pos = alien.offset_pos + pygame.Vector2(pulse, pulse)

                surface.blit(scaled_img, pos)
            elif alien.active and alien.health > 0:
                # Normal drawing
                alien.draw(surface, self.var_dict[alien.name][2])

    def draw_popups(self, screen, mouse_pos, event):
        """To be implemented by subclasses"""
        if self.level_completed and self.current_popup == "victory":
            popup_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 100, 500, 300)
            pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=10)
            pygame.draw.rect(screen, GREEN, popup_rect, 2, border_radius=10)

            # Title
            text = self.title_font.render("Mission Complete!", True, GREEN)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 20))

            # Stats
            stats_text = f"Eliminated {self.aliens_eliminated} aliens"
            stats_surface = self.menu_font.render(stats_text, True, WHITE)
            screen.blit(stats_surface, (popup_rect.centerx - stats_surface.get_width() // 2, popup_rect.centery - 20))

            continue_btn = Button(popup_rect.centerx - 75, popup_rect.bottom - 60, 160, 45,
                                  "Continue", BLUE, CYAN, self.menu_font)
            continue_btn.draw(screen)
            if continue_btn.is_clicked(mouse_pos, event):
                self.current_popup = None
                self.exit_to_levels = True

    def draw_panel(self, surface):
        """Draw full-screen command panel"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))
        self.draw_code_blocks(surface)
        self.run_button.draw(surface)
        self.reset_button.draw(surface)
        pygame.draw.rect(surface, RED, self.exit_button_rect)
        pygame.draw.line(surface, WHITE, self.exit_button_rect.topleft, self.exit_button_rect.bottomright, 4)
        pygame.draw.line(surface, WHITE, self.exit_button_rect.topright, self.exit_button_rect.bottomleft, 4)


    def draw_all(self, screen, mouse_pos, event):
        # Common drawing code
        pygame.draw.rect(screen, GRAY, self.battlefield, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.battlefield, 2, border_radius=5)
        #pygame.draw.rect(screen, RED, self.target, border_radius=3)
        #self.alien.pos = pygame.Vector2(self.alien.x, self.alien.y)
        #self.player.pos = pygame.Vector2(self.player.x, self.player.y)
        for alien in self.aliens:
            alien.draw(screen)
        #self.alien.draw_player(screen)
        self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.alien.draw_health_bar(screen)
        if self.level_id >= 3:
            self.player.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_popups(screen, mouse_pos, event)  # Delegate popups to subclasses

    def draw_elimination_counter(self, surface):
        """Draw the number of aliens eliminated"""
        counter_text = f"Aliens Eliminated: {self.aliens_eliminated}/{self.total_aliens_to_eliminate}"
        text_surface = self.menu_font.render(counter_text, True, WHITE)

        # Draw with background for readability
        bg_rect = pygame.Rect(10, 50, text_surface.get_width() + 20, text_surface.get_height() + 10)
        pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect, border_radius=5)
        pygame.draw.rect(surface, GREEN, bg_rect, 2, border_radius=5)

        surface.blit(text_surface, (bg_rect.x + 10, bg_rect.y + 5))

    def draw_game(self, screen, mouse_pos, event, frame_index):
        self.update_camera()
        self.draw_terrain(screen)

        # Update aliens and count eliminations
        eliminations = self.update_aliens()
        self.aliens_eliminated += eliminations

        # Check victory condition
        if self.aliens_eliminated >= self.total_aliens_to_eliminate and not self.level_completed:
            self.level_completed = True
            self.current_popup = "victory"

        # Draw game elements
        self.player.offset_pos = self.player.pos - self.camera_offset
        if self.curr_nearest_alien and self.curr_nearest_alien.active:
            direction = self.curr_nearest_alien.pos - self.player.pos
            self.player.angle = math.degrees(math.atan2(-direction.y, direction.x))

        if self.level_id == 2 and hasattr(self, 'draw_level_intro'):
            self.draw_level_intro(screen)

        self.draw_disappearing_aliens(screen)

        for alien in self.aliens:
            if not alien.disappearing:
                alien.offset_pos = alien.pos - self.camera_offset
                alien.draw_health_bar(screen)

        self.player.draw_player(screen, self.walk_frames[frame_index])
        self.run_button.draw(screen)
        self.reset_button.draw(screen)

        if self.level_id >= 3:
            self.player.draw_health_bar(screen)

        self.draw_bullets(screen)
        self.draw_minimap()
        self.draw_alien_dir()

        # Draw elimination counter
        self.draw_elimination_counter(screen)
        self.draw_popups(screen, mouse_pos, event)



