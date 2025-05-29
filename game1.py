import pygame
import sys
import math
import random

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
BULLET_SPEED = 10
BULLET_RADIUS = 5
TARGET_MAX_HEALTH = 200
DAMAGE_PER_HIT = 25


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


class Level:
    def __init__(self):
        # Common initialization code
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

        # Common commands
        self.commands = {
            "move": {"color": (0, 100, 200), "text": "Move Forward"},
            "turn_left": {"color": (200, 100, 0), "text": "Turn Left"},
            "turn_right": {"color": (20, 100, 0), "text": "Turn Right"},
            "reverse": {"color": (250, 100, 0), "text": "Reverse"},
            "shoot": {"color": (250, 100, 0), "text": "Shoot"}
        }

    def reset_level(self):
        self.__init__()

    def shoot_bullet(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_cooldown:
            return

        self.last_shot_time = current_time

        # Calculate bullet starting position (gun tip)
        gun_length = self.player_size * 1.5
        start_x = self.player_pos[0] + self.player_size // 2 + gun_length * math.sin(math.radians(self.player_angle))
        start_y = self.player_pos[1] + self.player_size // 2 - gun_length * math.cos(math.radians(self.player_angle))

        # Calculate direction vector
        angle_rad = math.radians(self.player_angle)
        dx = math.sin(angle_rad)
        dy = -math.cos(angle_rad)

        self.bullets.append({
            "x": start_x,
            "y": start_y,
            "dx": dx * BULLET_SPEED,
            "dy": dy * BULLET_SPEED,
            "radius": BULLET_RADIUS
        })

    def update_bullets(self):
        if not self.bullets:
            return

        bullets_to_remove = []

        for i, bullet in enumerate(self.bullets):
            # Update position
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

            # Check boundary collision
            if not self.battlefield.collidepoint(bullet["x"], bullet["y"]):
                bullets_to_remove.append(i)
                continue

            # Check if bullet touches target perimeter
            bullet_pos = (bullet["x"], bullet["y"])
            if self.check_perimeter_collision(bullet_pos):
                self.target_health = max(0, self.target_health - DAMAGE_PER_HIT)
                bullets_to_remove.append(i)

                if self.target_health <= 0:
                    self.current_popup = "shooting"

        # Remove bullets that hit or left battlefield
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)

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
        if not self.bullets:
            return
        for bullet in self.bullets:
            pygame.draw.circle(surface, ORANGE, (int(bullet["x"]), int(bullet["y"])), bullet["radius"])

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
        # Draw command blocks area
        pygame.draw.rect(surface, DARK_GRAY, self.commands_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.commands_area, 2, border_radius=5)

        # Draw available commands
        self.code_blocks.clear()
        for i, (cmd, props) in enumerate(self.commands.items()):
            rect = pygame.Rect(60 + i * 90, 15, 90, 25)
            pygame.draw.rect(surface, props["color"], rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=3)
            text = code_font.render(props["text"], True, WHITE)
            surface.blit(text, (rect.x + 5, rect.y + 5))
            self.code_blocks.append({"rect": rect, "type": cmd})

        # Draw main code area
        pygame.draw.rect(surface, DARK_GRAY, self.code_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.code_area, 2, border_radius=5)

        # Draw commands in main area
        y_offset = 110
        for cmd in self.main_code:
            if cmd["type"] == "for_loop":
                #print(cmd["iterations"])
                loop_rect = cmd["rect"]
                pygame.draw.rect(surface, FOR_LOOP_COLOR, cmd["rect"], border_radius=5)
                pygame.draw.rect(surface, WHITE, cmd["rect"], 2, border_radius=5)

                # Draw loop header with editable iteration count
                header_text = "Repeat "
                text_surf = code_font.render(header_text, True, WHITE)
                surface.blit(text_surf, (cmd["rect"].x + 10, cmd["rect"].y + 10))

                # Draw iteration input box
                iteration_box = pygame.Rect(
                    cmd["rect"].x + 10 + text_surf.get_width(),
                    cmd["rect"].y + 5,
                    40,
                    20
                        )
                pygame.draw.rect(surface, WHITE, iteration_box, 1)
                pygame.draw.rect(surface, BLACK, iteration_box)

                # Highlight if currently editing this loop
                # In draw_code_blocks, change the editing check to:
                if self.editing_loop_index is not None and self.main_code[self.editing_loop_index] == cmd:
                    pygame.draw.rect(surface, CYAN, iteration_box, 2)

                iteration_text = code_font.render(str(cmd["iterations"]), True, WHITE)
                surface.blit(iteration_text, (
                    iteration_box.x + (iteration_box.width - iteration_text.get_width()) // 2,
                    iteration_box.y + (iteration_box.height - iteration_text.get_height()) // 2
                        ))

                times_text = code_font.render("times:", True, WHITE)
                surface.blit(times_text, (
                iteration_box.x + iteration_box.width + 5,
                cmd["rect"].y + 10
                   ))

                # Draw drop zone highlight if dragging
                if self.dragging and loop_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surface, (255, 255, 255, 50), loop_rect, 2, border_radius=5)

                # Draw nested commands
                nested_y = loop_rect.y + 40
                #print(cmd["nested_commands"])
                for nested_cmd in cmd["nested_commands"]:

                    nested_rect = pygame.Rect(loop_rect.x + 20, nested_y, 160, 25)
                    pygame.draw.rect(surface, self.commands[nested_cmd["type"]]["color"],
                                     nested_rect, border_radius=3)
                    pygame.draw.rect(surface, WHITE, nested_rect, 1, border_radius=3)
                    text = code_font.render(self.commands[nested_cmd["type"]]["text"], True, WHITE)
                    surface.blit(text, (nested_rect.x + 5, nested_rect.y + 5))
                    nested_y += 30

                # Update loop block height based on content
                cmd["rect"].height = 40 + len(cmd["nested_commands"]) * 30
                y_offset += cmd["rect"].height + 10
            else:
                # Regular command
                cmd["rect"] = pygame.Rect(self.code_area.x + 20, y_offset, 210, 25)
                pygame.draw.rect(surface, self.commands[cmd["type"]]["color"], cmd["rect"], border_radius=3)
                pygame.draw.rect(surface, WHITE, cmd["rect"], 1, border_radius=3)
                text = code_font.render(self.commands[cmd["type"]]["text"], True, WHITE)
                surface.blit(text, (cmd["rect"].x + 5, cmd["rect"].y + 5))
                y_offset += 30

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

    def handle_events(self, event, mouse_pos):
        # Common event handling
        #print(self.editing_loop_index)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for block in self.code_blocks:
                if block["rect"].collidepoint(mouse_pos):
                    self.dragging = {
                        "type": block["type"],
                        "offset": (mouse_pos[0] - block["rect"].x,
                                   mouse_pos[1] - block["rect"].y)
                    }
                    return
            for i, cmd in enumerate(self.main_code):
                    if cmd["type"] == "for_loop":
                        # Calculate iteration box position
                        header_text = "Repeat "
                        text_width = code_font.size(header_text)[0]
                        iteration_box = pygame.Rect(
                            cmd["rect"].x + 10 + text_width,
                            cmd["rect"].y + 5,
                            40,
                            20
                        )

                        if iteration_box.collidepoint(mouse_pos):
                            #print(i)
                            self.editing_loop_index = i
                            #self.editing_text = str(cmd["iterations"])
                            return

                        else:
                            if hasattr(self, 'editing_loop'):
                                del self.editing_loop
                                self.editing_loop_index = None

              # If clicked outside any iteration box, stop editing
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            if self.code_area.collidepoint(mouse_pos):
                # Check if dropping onto an existing loop block
                for cmd in self.main_code:
                    if cmd["type"] == "for_loop" and cmd["rect"].collidepoint(mouse_pos):
                        # Calculate position within loop block
                        #print(234)
                        rel_y = mouse_pos[1] - cmd["rect"].y

                        # Only add if dropped below the header (y > 30)
                        if True:
                            nested_index = (rel_y - 40) // 30
                            nested_index = max(0, min(nested_index, len(cmd["nested_commands"])))

                            cmd["nested_commands"].insert(nested_index, {
                                "type": self.dragging["type"],
                                "pos": mouse_pos
                            })
                            self.dragging = None
                            return

                # Otherwise add to main code
                self.add_to_main_code(self.dragging["type"], mouse_pos)

            self.dragging = None

        elif event.type == pygame.KEYDOWN and self.editing_loop_index is not None:

            cmd = self.main_code[self.editing_loop_index]  # Get the actual loop block
            #print(cmd)
            if event.key == pygame.K_RETURN:

                if self.editing_text.isdigit() and int(self.editing_text) >= 0:
                    cmd["iterations"] = min(99, int(self.editing_text))

                self.editing_loop_index = None

            elif event.key == pygame.K_BACKSPACE:

                self.editing_text = self.editing_text[:-1]

            elif event.unicode.isdigit():
                if len(self.editing_text) < 2:
                    self.editing_text += event.unicode
                else:
                    self.editing_text = event.unicode

        if self.run_button.is_clicked(mouse_pos, event):
            self.execute_commands()

        if self.reset_button.is_clicked(mouse_pos, event):
            self.main_code = []

    def execute_commands(self):
        for cmd in self.main_code:
            if cmd["type"] == "for_loop":
                for _ in range(cmd["iterations"]):
                    for nested_cmd in cmd["nested_commands"]:
                        self.execute_command(nested_cmd)
            else:
                self.execute_command(cmd)

    def add_to_main_code(self, command_type, mouse_pos):
        """Add a command or loop block to main code"""
        # Calculate position in code area
        pos_in_area = (mouse_pos[0] - self.code_area.x, mouse_pos[1] - self.code_area.y)

        if command_type == "for_loop":
            # Find insertion point in main_code based on y position
            insert_index = len(self.main_code)
            for i, cmd in enumerate(self.main_code):
                if cmd["rect"].y > mouse_pos[1]:
                    insert_index = i
                    break

            self.main_code.insert(insert_index, {
                "type": "for_loop",
                "iterations": 3,
                "nested_commands": [],
                "rect": pygame.Rect(
                    self.code_area.x + 20,
                    self.code_area.y + 110 + insert_index * 60,  # Initial position
                    210,
                    60  # Initial height
                )
            })
        else:
            # Regular command - find insertion point
            insert_index = len(self.main_code)
            for i, cmd in enumerate(self.main_code):
                if cmd["rect"].y > mouse_pos[1]:
                    insert_index = i
                    break

            self.main_code.insert(insert_index, {
                "type": command_type,
                "rect": pygame.Rect(
                    self.code_area.x + 20,
                    self.code_area.y + 110 + insert_index * 30,
                    210,
                    25
                )
            })

        # Recalculate all positions to avoid overlaps
        self.recalculate_code_positions()

    def recalculate_code_positions(self):
        """Reposition all code blocks to avoid overlaps"""
        y_offset = 110
        for cmd in self.main_code:
            if cmd["type"] == "for_loop":
                cmd["rect"].y = y_offset
                cmd["rect"].height = 40 + len(cmd["nested_commands"]) * 30
                y_offset += cmd["rect"].height + 10
            else:
                cmd["rect"].y = y_offset
                y_offset += 30

    def draw_popups(self, screen, mouse_pos, event):
        """To be implemented by subclasses"""
        pass

    def draw_all(self, screen, mouse_pos, event):
        # Common drawing code
        pygame.draw.rect(screen, GRAY, self.battlefield, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.battlefield, 2, border_radius=5)
        pygame.draw.rect(screen, RED, self.target, border_radius=3)
        self.draw_player(screen)
        self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_popups(screen, mouse_pos, event)  # Delegate popups to subclasses

class Level1(Level):
    def __init__(self):
        super().__init__()
        # Level1 specific initialization
        """self.commands = {
            "move": {"color": (0, 100, 200), "text": "Move Forward"},
            "turn_left": {"color": (200, 100, 0), "text": "Turn Left"}
        }"""

    def draw_popups(self, screen, mouse_pos, event):
        if self.current_popup == "success":
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
                """self.commands.update({
                    "turn_right": {"color": (20, 100, 0), "text": "Turn Right"},
                    "reverse": {"color": (250, 100, 0), "text": "Reverse"}
                })"""

class Level2(Level):
    def __init__(self):
        super().__init__()
        # Level2 specific initialization
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}

    def draw_popups(self, screen, mouse_pos, event):
        if self.current_popup == "shooting":
            popup_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 300, 150)
            pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=10)
            pygame.draw.rect(screen, GREEN, popup_rect, 2, border_radius=10)

            text = title_font.render("Now use loops!", True, GREEN)
            screen.blit(text, (popup_rect.centerx - text.get_width() // 2, popup_rect.top + 20))

            continue_btn = Button(popup_rect.centerx - 75, popup_rect.top + 80, 150, 40,
                                 "Continue", BLUE, CYAN)
            continue_btn.draw(screen)
            if continue_btn.is_clicked(mouse_pos, event):
                self.current_popup = None
                #self.commands["shoot"] = {"color": (250, 100, 0), "text": "Shoot"}

start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start Game", BLUE, CYAN)
quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Quit", BLUE, CYAN)
level_selector = LevelSelector()
level1 = Level1()
level2 = Level2()

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


while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = clock.tick(60) / 1000

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


    elif current_state == STATE_LEVEL2:
        level2.draw_all(screen, mouse_pos, event)

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

        elif current_state == STATE_LEVEL1:
            level1.handle_events(event, mouse_pos)
            level1.update_bullets()
            if level1.level_state == 0:
                current_state = STATE_LEVELS
                #level1.success_popup = False
                #level1.success_popup1 = False

        elif current_state == STATE_LEVEL2:
            #level2.draw_all()
            level2.handle_events(event, mouse_pos)
            level2.update_bullets()
            if level2.level_state == 0:
                current_state = STATE_LEVELS
                level2.current_popup = " "

    # Update

    pygame.display.flip()

pygame.quit()
sys.exit()