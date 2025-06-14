from queue import Queue

import pygame
import sys
import math
import random
import time
import copy

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AstroCode")

# Game states
STATE_START = 0
STATE_LEVELS = 1
STATE_LEVEL1 = 2
STATE_LEVEL2 = 3
STATE_LEVEL3 = 4
STATE_LEVEL4 = 5
current_state = STATE_START

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
PURPLE = (150, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
FOR_LOOP_COLOR = PURPLE

# Fonts
title_font = pygame.font.Font(None, 72)
menu_font = pygame.font.Font(None, 48)
subtitle_font = pygame.font.Font(None, 36)
level_font = pygame.font.Font(None, 36)
code_font = pygame.font.Font(None, 18)

# Starfield background
stars = []
for _ in range(200):
    x = pygame.math.Vector2(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )
    speed = random.uniform(0.1, 0.5)
    size = random.randint(1, 3)
    stars.append((x, speed, size))

# Twinkling effect variables
twinkle_timer = 0
twinkle_delay = 0.1
BULLET_SPEED = 180
dt = 0
BULLET_RADIUS = 5
TARGET_MAX_HEALTH = 200
DAMAGE_PER_HIT = 25
PLAYER_AWARENESS_RANGE = 500


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text_surf = menu_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class LevelSelector:
    def __init__(self):
        self.levels = []
        self.back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back", BLUE, CYAN)

        # Create level buttons grid
        button_size = 60
        padding = 20
        start_x = WIDTH // 2 - (2 * button_size + padding)
        start_y = HEIGHT // 4

        for i in range(10):
            row = i // 5
            col = i % 5
            x = start_x + col * (button_size + padding)
            y = start_y + row * (button_size + padding)
            btn = Button(x, y, button_size, button_size, str(i + 1), BLUE, GREEN)
            self.levels.append(btn)

    def draw(self, surface):
        title_text = title_font.render("Select Level", True, CYAN)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        surface.blit(title_text, title_rect)

        for btn in self.levels:
            btn.draw(surface)

        self.back_button.draw(surface)

    def handle_click(self, pos, event):
        for i, btn in enumerate(self.levels):
            if btn.is_clicked(pos, event):
                return i + 1

        if self.back_button.is_clicked(pos, event):
            global current_state
            current_state = STATE_START

        return None


bullet_pool = []
bullet_options = []


class Bullet:
    __slots__ = ('x', 'y', 'dx', 'dy', 'radius', 'active', 'shape')  # Faster attribute access

    def __init__(self, x=None, y=None, dx=None, dy=None, radius=None, active=False, shape="circle"):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.active = active
        self.shape = shape

    def draw(self):
        """Draw the bullet based on its shape type"""
        if self.shape == "circle":
            self.draw_circle()
        elif self.shape == "square":
            self.draw_square()
        elif self.shape == "triangle":
            self.draw_triangle()

    def draw_circle(self):
        """Draw circular bullet (original implementation)"""
        bullet_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surface, ORANGE, (self.radius, self.radius), self.radius)
        screen.blit(bullet_surface, (self.x - self.radius, self.y - self.radius))

    def draw_square(self):
        """Draw square bullet"""
        size = self.radius * 2  # Square side length
        bullet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(
            bullet_surface,
            BLUE,  # Different color for squares
            (0, 0, size, size),
            border_radius=0  # Slightly rounded corners
        )
        screen.blit(bullet_surface, (self.x - self.radius, self.y - self.radius))

    def draw_triangle(self):
        """Draw triangular bullet"""
        height = self.radius * 2
        width = height * 0.866  # Equilateral triangle ratio

        bullet_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Triangle points (equilateral)
        points = [
            (width // 2, 0),  # Top point
            (0, height),  # Bottom left
            (width, height)  # Bottom right
        ]

        pygame.draw.polygon(
            bullet_surface,
            GREEN,  # Different color for triangles
            points
        )
        screen.blit(bullet_surface, (self.x - width // 2, self.y - height // 2))

main_code_height = 0

class Command:
    def __init__(self, cmd_type, iterations=1, nested_commands=None, rect=None, conditions=None, condition_var=None,
                 condition_op=None, condition_val=None, editing_condition_part=None):
        self.cmd_type = cmd_type
        self.iterations = iterations
        self.conditions = conditions if conditions is not None else {}
        self.nested_commands = nested_commands if nested_commands is not None else []
        self.rect = rect
        self.condition_var = condition_var  # e.g. "health"
        self.condition_op = condition_op  # e.g. ">"
        self.condition_val = condition_val  # e.g. "50"
        self.editing_condition_part = editing_condition_part  # Tracks which box is being edited
        self.shoot_target_shape = Circle(0, 0, 8, WHITE)  # Stores the shape (Circle, Square, Triangle) for shoot target
        self.shoot_target_box_rect = None

        # Command properties (previously in the dictionary)
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
        return colors.get(self.cmd_type, (100, 100, 100))  # Default gray

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
        return self.cmd_type == ("if_statement" or "else_statement")

    def draw(self, surface, x, y, width, indent=0, is_nested=False):
        global main_code_height
        """Recursively draw the command and its nested commands"""
        # Set the command's rectangle
        if self.rect is None:
            self.rect = pygame.Rect(
                x + indent,
                y,
                width - indent,
                25 if not self.is_loop() else 40  # Base height
            )
        #self.rect.y += main_code_height
        # Draw the command itself
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)

        if self.is_loop() or self.is_conditional() or self.cmd_type == "while_loop":
            # Draw loop header
            if self.is_loop():
                self._draw_loop_header(surface)
            elif self.is_conditional():
                self._draw_conditional_header("if", surface)
            else:
                self._draw_regular_command(surface)

            # Recursively draw nested commands
            nested_y = y + 40
            for nested_cmd in self.nested_commands:
                nested_height = nested_cmd.draw(
                    surface,
                    x,
                    nested_y,
                    width - 20,  # Reduce width for nesting
                    indent + 20,  # Add indentation
                    True  # Mark as nested
                )
                nested_y += nested_height

            # Update the loop block's total height
            self.rect.height = max(40, nested_y - y)
            #self._draw_loop_header(surface)
            #pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
            #pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)
            #self._draw_loop_header(surface)
        elif self.cmd_type == "shoot":
            self._draw_shoot_command_content(surface)

        else:
            # Draw regular command text
            self._draw_regular_command(surface)
            #pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
            #pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)

        #main_code_height += self.rect.height

        return self.rect.height

    def _draw_regular_command(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)
        text = code_font.render(self.text, True, WHITE)
        surface.blit(text, (self.rect.x + 5, self.rect.y + 5))

    def _draw_loop_header(self, surface):
        """Draw the header part of a loop block with iteration count"""
        # Draw "Repeat X times" header
        header_text = "Repeat"
        text_surf = code_font.render(header_text, True, WHITE)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

        # Create iteration count box
        box_start_x = self.rect.x + 10 + text_surf.get_width() + 10
        box_width = 60
        box_height = 20
        box_y = self.rect.y + 5
        iter_box = pygame.Rect(box_start_x, box_y, box_width, box_height)

        # Draw the box
        pygame.draw.rect(surface, BLACK, iter_box)
        pygame.draw.rect(surface, WHITE, iter_box, 1)

        # Draw the iteration number (centered)
        iter_text = str(self.iterations)
        iter_surf = code_font.render(iter_text, True, WHITE)
        iter_rect = iter_surf.get_rect(center=iter_box.center)
        surface.blit(iter_surf, iter_rect)

        # Draw "times" text after the box
        times_text = "times"
        text_surf_1 = code_font.render(times_text, True, WHITE)
        surface.blit(text_surf_1, (box_start_x + box_width + 10, self.rect.y + 10))

    def _draw_conditional_header(self, txt, surface):
        """Draw the header part of an if-block with condition boxes"""
        # Draw the main if-block header background
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)

        # Draw "if" text
        if_text = code_font.render(txt, True, WHITE)
        surface.blit(if_text, (self.rect.x + 10, self.rect.y + 10))

        # Calculate positions for condition boxes
        box_start_x = self.rect.x + 10 + if_text.get_width() + 10
        box_width = 60  # Width for variable and value boxes
        op_width = 30  # Width for operator box
        box_height = 20
        box_y = self.rect.y + 5

        # 1. Variable box (left)
        var_box = pygame.Rect(box_start_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, BLACK, var_box)
        pygame.draw.rect(surface, WHITE, var_box, 1)

        # Draw variable name if it exists
        if hasattr(self, 'condition_var') and self.condition_var:
            var_text = code_font.render(self.condition_var, True, WHITE)
            surface.blit(var_text, (var_box.x + 5, var_box.y + 3))

        # 2. Operator box (middle)
        op_box = pygame.Rect(box_start_x + box_width + 5, box_y, op_width, box_height)
        pygame.draw.rect(surface, BLACK, op_box)
        pygame.draw.rect(surface, WHITE, op_box, 1)

        # Draw operator if it exists
        if hasattr(self, 'condition_op') and self.condition_op:
            op_text = code_font.render(self.condition_op, True, WHITE)
            surface.blit(op_text, (op_box.x + 5, op_box.y + 3))

        # 3. Value box (right)
        val_box = pygame.Rect(box_start_x + box_width + op_width + 10, box_y, box_width, box_height)
        pygame.draw.rect(surface, BLACK, val_box)
        pygame.draw.rect(surface, WHITE, val_box, 1)

        # Draw value if it exists
        if hasattr(self, 'condition_val') and self.condition_val:
            #val_text = code_font.render(str(self.condition_val), True, WHITE)
            #surface.blit(val_text, (val_box.x + 5, val_box.y + 3))
            self.condition_val.x = val_box.centerx
            self.condition_val.y = val_box.centery
            self.condition_val.draw(surface)

        # Add edit cursor if currently editing
        if hasattr(self, 'editing_condition_part'):
            cursor_box = {
                'var': var_box,
                'op': op_box,
                'val': val_box
            }.get(self.editing_condition_part)

            if cursor_box:
                pygame.draw.rect(surface, CYAN, cursor_box, 2)

    def _draw_shoot_command_content(self, surface):
        """Draw the content for a 'shoot' command with a target shape box."""
        # Draw "Shoot" text
        shoot_text = code_font.render(self.text, True, WHITE)  # self.text will be "Shoot"
        surface.blit(shoot_text, (self.rect.x + 5, self.rect.y + 5))

        # Calculate position for the new target box
        box_width = 30  # Example size for the target box
        box_height = 20
        # Position it right next to the "Shoot" text
        box_x = self.rect.x + 5 + shoot_text.get_width() + 10
        box_y = self.rect.y + 5

        self.shoot_target_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        # Draw the target box background and border
        pygame.draw.rect(surface, BLACK, self.shoot_target_box_rect)
        pygame.draw.rect(surface, WHITE, self.shoot_target_box_rect, 1)

        # Draw the shape if it exists
        if self.shoot_target_shape:
            self.shoot_target_shape.x = self.shoot_target_box_rect.centerx
            self.shoot_target_shape.y = self.shoot_target_box_rect.centery
            # Adjust shape size if necessary to fit the box
            # For example, if your shapes have a 'set_size' method:
            # shape_display_size = min(self.shoot_target_box_rect.width, self.shoot_target_box_rect.height) * 0.8
            # self.shoot_target_shape.set_size(shape_display_size)
            self.shoot_target_shape.draw(surface)


class Player:
    def __init__(self, x=0, y=0, width=0, height=0, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.width = width
        self.height = height
        self.bullets = []
        self.max_bullets = 50
        self.bullet_pool = []
        self.current_bullet = None
        self.damage_dealt = False
        self.health = 200
        self.color = CYAN

    def draw_player(self, surface):
        # Player body
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, body_rect)

        # Gun (rotated based on angle)
        gun_length = self.height * 1.5
        gun_center = (body_rect.centerx, body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    def _init_bullet(self, bullet, x, y, angle, width, height):
        """Initialize bullet properties"""
        angle_rad = math.radians(angle)
        center_x = x + width // 2
        center_y = y + height // 2
        gun_length = height * 1.5

        bullet.x = center_x + gun_length * math.sin(angle_rad)
        bullet.y = center_y - gun_length * math.cos(angle_rad)
        bullet.dx = math.sin(angle_rad)
        bullet.dy = -math.cos(angle_rad)
        bullet.radius = BULLET_RADIUS
        bullet.active = True

    def shoot_bullet(self, shape):
        # current_time = pygame.time.get_ticks()
        # print(current_time)
        # if current_time - self.last_shot_time < self.shot_cooldown:
        # return

        # self.last_shot_time = current_time

        # Reuse inactive bullets first
        for bullet in self.bullet_pool:
            if not bullet.active:
                self._init_bullet(bullet, self.x, self.y, self.angle, self.width, self.height)
                return

        # Create new bullet if pool is empty
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(shape=shape)
            self._init_bullet(bullet, self.x, self.y, self.angle, self.width, self.height)
            self.bullets.append(bullet)

    def update_bullets(self, target, level_id):
        self.damage_dealt = False
        #target = self.target  # Cache target reference

        for bullet in self.bullets:
            if not bullet.active:
                continue

            # Update position
            bullet.x += bullet.dx * dt * BULLET_SPEED
            bullet.y += bullet.dy * dt * BULLET_SPEED
            #self.current_bullet = bullet

            # Boundary check
            if not (0 <= bullet.x < WIDTH and 0 <= bullet.y < HEIGHT):
                bullet.active = False
                continue

            # Fast AABB collision check
            if (target.x - BULLET_RADIUS <= bullet.x <= target.x + target.width + BULLET_RADIUS and
                    target.y - BULLET_RADIUS <= bullet.y <= target.y + target.height + BULLET_RADIUS):
                bullet.active = False
                self.damage_dealt = True

        # Remove inactive bullets (do this less frequently)
        if random.random() < 0.1:  # Only clean up 10% of frames
            self.bullets = [b for b in self.bullets if b.active]
            self.bullet_pool = [b for b in self.bullets if not b.active]
        self.bullets = [b for b in self.bullets if b.active]

        if self.damage_dealt:
            if level_id == 1 or level_id == 2:
                target.health = max(0, target.health - DAMAGE_PER_HIT)


    def draw_health_bar(self, surface):
        bar_width = self.width
        bar_height = 10
        bar_x = self.x
        bar_y = self.y - bar_height - 5

        # Background
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))

        # Health level
        health_width = (self.health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))

        # Border
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)


class Alien(Player):
    def __init__(self):
        super().__init__()
        self.x = 60
        self.y = 170
        self.angle = 90
        self.width = 60
        self.height = 60
        self.shape_options = ["circle", "square", "triangle"]
        self.prev_time = 0
        self.color = RED

    def shoot_alien_bullets(self):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.prev_time >= 800:
            self.shoot_bullet(self.shape_options[random.randint(0, 2)])
            self.prev_time = curr_time


class Level:
    def __init__(self):
        # Common initialization code
        global main_code_height
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
        self.run_button = Button(637, 550, 100, 40, "Run", GREEN, (0, 200, 0))
        self.reset_button = Button(513, 550, 100, 40, "Reset", RED, (200, 0, 0))
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

    def reset_level(self):
        self.__init__()
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
        self.player.update_bullets(self.alien, self.level_id)
        if self.level_id == 3:
            self.alien.update_bullets(self.player, self.level_id)
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

    def check_perimeter_collision(self, point):
        """Check if a point touches the target's perimeter"""
        X, y = point
        target = self.target
        tolerance = self.bullets[0]["radius"]  # Use bullet radius as collision threshold

        # Check if point is near any of the four edges
        left_edge = abs(X - target.left) <= tolerance
        right_edge = abs(X - target.right) <= tolerance
        top_edge = abs(y - target.top) <= tolerance
        bottom_edge = abs(y - target.bottom) <= tolerance

        # Check vertical edges (left/right)
        if (left_edge or right_edge) and (target.top - tolerance <= y <= target.bottom + tolerance):
            return True

        # Check horizontal edges (top/bottom)
        if (top_edge or bottom_edge) and (target.left - tolerance <= X <= target.right + tolerance):
            return True

        # Check corners (optional, for more precise collision)
        corner_radius = tolerance
        corners = [
            (target.left, target.top),  # Top-left
            (target.right, target.top),  # Top-right
            (target.left, target.bottom),  # Bottom-left
            (target.right, target.bottom)  # Bottom-right
        ]

        for corner_x, corner_y in corners:
            if math.sqrt((X - corner_x) ** 2 + (y - corner_y) ** 2) <= corner_radius:
                return True

        return False

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
                bullet.draw()
        if self.alien.bullets and self.level_id == 3:
            for bullet in self.alien.bullets:
                bullet.draw()

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
            text = code_font.render(cmd.text, True, WHITE)
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

    def check_collision(self):
        # Calculate gun tip position
        gun_length = self.player_size * 1.5
        gun_tip_x = self.player_pos[0] + self.player_size // 2 + gun_length * math.sin(math.radians(self.player_angle))
        gun_tip_y = self.player_pos[1] + self.player_size // 2 - gun_length * math.cos(math.radians(self.player_angle))

        # Check if point lies exactly on the rectangle's perimeter
        target_rect = self.target

        # Check left or right edges (with x coordinate matching and y within range)
        if (math.isclose(gun_tip_x, target_rect.left) or math.isclose(gun_tip_x, target_rect.right)):
            if target_rect.top <= gun_tip_y <= target_rect.bottom:
                return True

        # Check top or bottom edges (with y coordinate matching and x within range)
        if (math.isclose(gun_tip_y, target_rect.top) or math.isclose(gun_tip_y, target_rect.bottom)):
            if target_rect.left <= gun_tip_x <= target_rect.right:
                return True

        return False

    def in_range(self):
        # Calculate gun tip position
        gun_length = self.player_size * 1.5
        gun_tip_x = self.player_pos[0] + self.player_size // 2 + gun_length * math.sin(math.radians(self.player_angle))
        gun_tip_y = self.player_pos[1] + self.player_size // 2 - gun_length * math.cos(math.radians(self.player_angle))

        # Get target edges
        left = self.target.left
        right = self.target.right
        top = self.target.top
        bottom = self.target.bottom

        # Find the closest point on target perimeter to gun tip
        closest_x = max(left, min(gun_tip_x, right))
        closest_y = max(top, min(gun_tip_y, bottom))
        # If gun tip is inside target, find edge distance
        if (left <= gun_tip_x <= right) and (top <= gun_tip_y <= bottom):
            # Inside the target - find distance to nearest edge
            dist_left = gun_tip_x - left
            dist_right = right - gun_tip_x
            dist_top = gun_tip_y - top
            dist_bottom = bottom - gun_tip_y
            min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
            return min_dist < 40
        else:
            # Outside the target - calculate distance to perimeter
            if closest_x == left or closest_x == right:
                # Closest to vertical edge
                dist_x = abs(gun_tip_x - closest_x)
                dist_y = abs(gun_tip_y - closest_y)
                return math.sqrt(dist_x ** 2 + dist_y ** 2) < 40
            else:
                # Closest to horizontal edge
                dist_x = abs(gun_tip_x - closest_x)
                dist_y = abs(gun_tip_y - closest_y)
                return math.sqrt(dist_x ** 2 + dist_y ** 2) < 40

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
        if_text = code_font.render("if", True, WHITE)
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
                                              "type"] != "for_loop" or "if_statement" or "while_loop" else 40
                                )
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
        text_width = code_font.size(header_text)[0]
        return pygame.Rect(
            cmd.rect.x + 10 + text_width,
            cmd.rect.y + 5,
            60,
            20
        )

    def execute_commands(self, cmd_list):
        step_delay = 0
        for cmd in cmd_list:
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
                """while True:
                    self.command_queue[:0] = cmd.nested_commands
                    self.update_commands(dt)"""
                pass

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
                )
            )
        elif command_type == "if_statement" or command_type == "while_loop":
            new_cmd = Command(
                cmd_type=command_type,
                iterations=1,
                nested_commands=[],
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    60
                ),
                conditions={}
            )

        else:
            new_cmd = Command(
                cmd_type=command_type,
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    25 # Initial height
                )
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

            text = title_font.render("Good Job!", True, GREEN)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 20))

            continue_btn = Button(popup_rect.centerx - 75, popup_rect.top + 80, 150, 40,
                                  "Continue", BLUE, CYAN)
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

            text = title_font.render("The aliens killed you!", True, GREEN)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 20))

            continue_btn = Button(popup_rect.centerx - 75, popup_rect.top + 80, 150, 40,
                                  "Continue", BLUE, CYAN)
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


class Level1(Level):
    def __init__(self):
        super().__init__()
        self.level_id = 1
        # Level1 specific initialization


class Level2(Level):
    def __init__(self):
        super().__init__()
        self.level_id = 2
        # Level2 specific initialization
        self.code_blocks = []
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        super()._init_commands()


class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.shape = "circle"

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# --- Square Class ---
class Square:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.shape = "square"

    def draw(self, surface):
        # The rect should be centered around self.x, self.y
        top_left_x = self.x - self.size // 2
        top_left_y = self.y - self.size // 2
        pygame.draw.rect(surface, self.color, (top_left_x, top_left_y, self.size, self.size))

# --- Triangle Class ---
class Triangle:
    def __init__(self, x, y, size, color): # Assuming 'size' helps determine dimensions
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.shape = "triangle"
        # Define vertices relative to (0,0) and then translate
        # Example: equilateral triangle pointing up
        # You might need to adjust these points based on how you want your triangle oriented
        self.points_relative = [
            (0, -size / 2),
            (-size / 2, size / 2),
            (size / 2, size / 2)
        ]

    def draw(self, surface):
        # Translate the relative points to the current (self.x, self.y)
        translated_points = [(self.x + p[0], self.y + p[1]) for p in self.points_relative]
        pygame.draw.polygon(surface, self.color, translated_points)


class Level3(Level):
    def __init__(self):
        super().__init__()
        self.level_id = 3
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
            if cmd.is_loop() or cmd.is_conditional():
                # If a click is handled by a nested command, propagate True
                if self._process_command_clicks_recursive(mouse_pos, cmd.nested_commands):
                    return True  # Click handled by a nested command

        return False  # No click handled in this list or its descendants

class Level4(Level3):
    def __init__(self):
        super().__init__()
        self.level_id = 4
        self.code_blocks = []
        self.commands["while_loop"] = {"color": FOR_LOOP_COLOR, "text": "while"}
        super()._init_commands()


start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start Game", BLUE, CYAN)
quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Quit", BLUE, CYAN)
level_selector = LevelSelector()
level1 = Level1()
level2 = Level2()
level3 = Level3()
level4 = Level4()

# Main game loop
clock = pygame.time.Clock()
running = True


def draw_starfield():
    for pos, speed, size in stars:
        alpha = int(100 + 155 * (1 - speed))
        color = (alpha, alpha, alpha)
        pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), size)


def update_starfield(dt):
    global twinkle_timer
    for i, (pos, speed, size) in enumerate(stars):
        pos.x += speed * 10 * dt
        if pos.x > WIDTH:
            pos.x = 0
            pos.y = random.randint(0, HEIGHT)
        stars[i] = (pos, speed, size)

    twinkle_timer += dt
    if twinkle_timer >= twinkle_delay:
        twinkle_timer = 0
        for _ in range(5):
            idx = random.randint(0, len(stars) - 1)
            stars[idx] = (stars[idx][0], stars[idx][1], random.randint(1, 3))


FPS = 60
prev_time = time.time()
x = 0

while running:
    mouse_pos = pygame.mouse.get_pos()
    current_time = time.time()
    dt = (current_time - prev_time)  # Convert to seconds
    #print(dt)
    prev_time = current_time

    #update_starfield(dt)

    if current_state == STATE_START:
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
    elif current_state == STATE_LEVELS:
        for btn in level_selector.levels:
            btn.check_hover(mouse_pos)
        level_selector.back_button.check_hover(mouse_pos)
    elif current_state == STATE_LEVEL1:
        level1.run_button.check_hover(mouse_pos)
        level1.reset_button.check_hover(mouse_pos)

    # Draw
    screen.fill(BLACK)
    draw_starfield()

    if current_state == STATE_START:
        update_starfield(dt)
        # Draw title
        title_text = title_font.render("ASTROCODE", True, CYAN)
        title_shadow = title_font.render("ASTROCODE", True, PURPLE)
        pulse = math.sin(pygame.time.get_ticks() * 0.001) * 0.1 + 1
        scaled_title = pygame.transform.scale_by(title_text, pulse)
        scaled_shadow = pygame.transform.scale_by(title_shadow, pulse)
        scaled_rect = scaled_title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        screen.blit(scaled_shadow, (scaled_rect.x + 5, scaled_rect.y + 5))
        screen.blit(scaled_title, scaled_rect)

        # Draw subtitle
        subtitle_text = subtitle_font.render("A Cosmic Coding Adventure", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 70))
        screen.blit(subtitle_text, subtitle_rect)

        # Draw buttons
        start_button.draw(screen)
        quit_button.draw(screen)

        # Version info
        version_text = subtitle_font.render("v1.0", True, (100, 100, 100))
        screen.blit(version_text, (WIDTH - 80, HEIGHT - 40))

    elif current_state == STATE_LEVELS:
        level_selector.draw(screen)

    elif current_state == STATE_LEVEL1:
        level1.draw_all(screen, mouse_pos, event)
        #level1.alien.shoot_alien_bullets()
        try:
            next(level1.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level1.update(dt)

    elif current_state == STATE_LEVEL2:
        level2.draw_all(screen, mouse_pos, event)
        #level2.alien.shoot_alien_bullets()
        try:
            next(level2.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level2.update(dt)

    elif current_state == STATE_LEVEL3:
        level3.draw_all(screen, mouse_pos, event)
        if -20 < (level3.alien.y + level3.alien.height / 2) - (level3.player.y + level3.player.height / 2) < 20:
            level3.alien.shoot_alien_bullets()
        try:
            next(level3.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level3.update(dt)

    elif current_state == STATE_LEVEL4:
        level4.draw_all(screen, mouse_pos, event)
        if -20 < (level4.alien.y + level4.alien.height / 2) - (level4.player.y + level4.player.height / 2) < 20:
            level4.alien.shoot_alien_bullets()
        try:
            next(level4.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level4.update(dt)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == STATE_START:
            if start_button.is_clicked(mouse_pos, event):
                current_state = STATE_LEVELS
            if quit_button.is_clicked(mouse_pos, event):
                running = False

        elif current_state == STATE_LEVELS:
            selected_level = level_selector.handle_click(mouse_pos, event)
            if selected_level == 1:
                current_state = STATE_LEVEL1
                level1.reset_level()
            elif selected_level == 2:
                current_state = STATE_LEVEL2
                level2.reset_level()
            elif selected_level == 3:
                current_state = STATE_LEVEL3
                level3.reset_level()
            elif selected_level == 4:
                current_state = STATE_LEVEL4
                level4.reset_level()

        elif current_state == STATE_LEVEL1:
            level1.handle_events(event, mouse_pos)
            #level1.update_bullets(dt)
            if level1.exit_to_levels:
                current_state = STATE_LEVELS
                level1.exit_to_levels = False
                #level1.success_popup = False
                #level1.success_popup1 = False

        elif current_state == STATE_LEVEL2:
            #level2.draw_all()
            level2.handle_events(event, mouse_pos)

            if level2.exit_to_levels:
                current_state = STATE_LEVELS
                level2.exit_to_levels = False

        elif current_state == STATE_LEVEL3:
            level3.handle_events(event, mouse_pos)

            if level3.exit_to_levels:
                current_state = STATE_LEVELS
                level3.exit_to_levels = False

        elif current_state == STATE_LEVEL4:
            level4.handle_events(event, mouse_pos)

            if level4.exit_to_levels:
                current_state = STATE_LEVELS
                level4.exit_to_levels = False

    # Update

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
