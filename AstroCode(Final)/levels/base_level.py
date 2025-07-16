# Base class shared by all levels
import pygame
import math
import collections
import copy
import random
import os

from core.constants import (
    WIDTH, HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, CYAN, ORANGE,
    FOR_LOOP_COLOR, BULLET_RADIUS, TARGET_MAX_HEALTH, PLAYER_MAX_HEALTH,
    DAMAGE_PER_HIT, PLAYER_AWARENESS_RANGE, COMMAND_DELAY_MS, screen, ORIGINAL_CMD_WIDTH, ORIGINAL_CMD_HEIGHT_LOOP, ALIEN_TYPES, DARK_OVERLAY_COLOR
)
#from game1 import code_font
from ui.button import Button
from entities.player import Player
from entities.alien import Alien
from entities.bullet import Bullet
from entities.commands import Command
from entities.bullet_shapes import Circle, Square, Triangle# Import shape classes

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
        #self.alien = Alien(8000, 8000, "Alien Type A")
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
        #self.spawn_aliens(3)

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
            pygame.draw.circle(screen, ALIEN_TYPES[alien.name],
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

                # Draw arrow pointing to alien
                pygame.draw.circle(screen, ALIEN_TYPES[alien.name],
                                   (int(indicator_pos.x), int(indicator_pos.y)), 10)
                pygame.draw.line(screen, ALIEN_TYPES[alien.name],
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

    def update(self, dt):
        pass
        """Call this every frame from your main game loop"""
        #self.player.update_bullets(self.alien, self.level_id, dt)
        """"if self.level_id >= 3:
            self.alien.update_bullets(self.player, self.level_id, dt)
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
        self.alien.bullets = [b for b in self.alien.bullets if b.active]""" # Re-filter alien bullets too

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
        if self.player.bullets:
            for bullet in self.player.bullets:
                bullet.draw(surface, self.camera_offset)
        for alien in self.aliens:
            if alien.bullets:
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
        a = 0
        b = 0
        # Handle mouse button down events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on command palette
            for block in self.code_blocks:
                if block.rect:
                    if block.rect.collidepoint(mouse_pos):
                        self.dragging = {
                            "type": block.cmd_type,
                            "offset": (mouse_pos[0] - block.rect.x,
                                       mouse_pos[1] - block.rect.y)
                        }
                        return

            if self.player.body_rect.collidepoint(mouse_pos):
                self.code_editor = True
                self.game_view = False

        # Handle mouse button up (dropping commands)
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            if self.code_area.collidepoint(mouse_pos):
                # Check if dropping onto an existing loop block
                self.handle_cmd_drop(self.main_code, mouse_pos, 0, None)
            self.dragging = None


        elif event.type == pygame.KEYDOWN:

            if self.editing_loop_cmd is not None:
                Cmd = self.editing_loop_cmd

                if event.key == pygame.K_RETURN:
                    if Cmd.editing_text.isdigit() and int(Cmd.editing_text) > 0:
                        Cmd.iterations = min(99, int(Cmd.editing_text))
                    self.editing_loop_cmd = None
                elif event.key == pygame.K_BACKSPACE:
                    Cmd.editing_text = Cmd.editing_text[:-1]
                elif event.unicode.isdigit():
                    if len(Cmd.editing_text) < 2:
                        Cmd.editing_text += event.unicode
                    else:
                        Cmd.editing_text = ""

        # Handle run button
        if self.run_button.is_clicked(mouse_pos, event):
            """if not self.command_queue:
                self.command_queue = self.main_code.copy()
            self.current_command = None"""
            self.code_editor = False
            self.game_view = True
            self.cmd_gen = self.execute_commands(self.main_code, None)

            #self.execute_commands(self.main_code, screen, mouse_pos, event)

        # Handle reset button
        if self.reset_button.is_clicked(mouse_pos, event):
            self.main_code = []
            main_code_height = 0
            #self.recalculate_code_positions()

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
                    # Find nearest alien if none is currently targeted
                    if not self.curr_nearest_alien or not self.curr_nearest_alien.active:
                        self._update_nearest_alien()

                    # Only shoot if there's a valid target
                    if self.curr_nearest_alien:
                        bullet_type = cmd.shoot_bullet_type
                        color = ALIEN_TYPES.get(f"Alien {bullet_type}", ORANGE)  # Fallback color
                        self.player.shoot_bullet(
                            bullet_type=bullet_type,
                            alien_pos=self.curr_nearest_alien.pos,
                            color=color
                        )
                    else:
                        print("No valid target to shoot at!")
                yield

            #pygame.time.wait(step_delay)
                #screen.fill(BLACK)
            #self.draw_all(screen, mouse_pos, event)
            #pygame.display.update()

    def _update_nearest_alien(self):
        """Updates the nearest active alien to target"""
        self.curr_nearest_alien = None
        min_dist = float('inf')

        for alien in self.aliens:
            # First check if the alien has the 'active' attribute
            if not hasattr(alien, 'active'):
                alien.active = True  # Initialize if missing

            if not alien.active:
                continue

            dist = (alien.pos - self.player.pos).length()
            if dist < min_dist:
                min_dist = dist
                self.curr_nearest_alien = alien

        # Optional: Add a maximum targeting range
        if min_dist > 1000:  # Adjust this value as needed
            self.curr_nearest_alien = None


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

    def draw_panel(self, surface):
        """Draw full-screen command panel"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))
        #self.draw_command_column(surface)
        #self.draw_execution_column(surface)
        self.draw_code_blocks(surface)

        # Draw Run/Reset/Clear buttons only when panel is visible
        self.run_button.draw(surface)
        self.reset_button.draw(surface)
        #self.clear_button.draw(surface)
        # Draw exit button
        #self.exit_button.draw(surface)

    def draw_all(self, screen, mouse_pos, event):
        # Common drawing code
        pygame.draw.rect(screen, GRAY, self.battlefield, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.battlefield, 2, border_radius=5)
        #pygame.draw.rect(screen, RED, self.target, border_radius=3)
        #self.alien.pos = pygame.Vector2(self.alien.x, self.alien.y)
        #self.player.pos = pygame.Vector2(self.player.x, self.player.y)
        for alien in self.aliens:
            alien.draw_player(screen)
        #self.alien.draw_player(screen)
        self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.alien.draw_health_bar(screen)
        if self.level_id >= 3:
            self.player.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_popups(screen, mouse_pos, event)  # Delegate popups to subclasses

    def draw_game(self, screen, mouse_pos, event, frame_index):
        self.update_camera()
        self.draw_terrain(screen)
        #self.draw_minimap()
        #self.draw_alien_dir()
        self.player.offset_pos = self.player.pos - self.camera_offset
        for alien in self.aliens:
            alien.offset_pos = alien.pos - self.camera_offset
            alien.draw_player(screen, self.var_dict[alien.name][2])
            alien.draw_health_bar(screen)
        #self.alien.draw_player(screen)
        #self.player.draw_player(screen)
        self.player.draw_player(screen, self.walk_frames[frame_index])
        #self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        if self.level_id >= 3:
            self.player.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_minimap()
        self.draw_alien_dir()
        #self.draw_popups(screen, mouse_pos, event)


# --- Level Specific Implementations ---
