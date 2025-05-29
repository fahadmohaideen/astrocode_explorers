import pygame
import sys
import math
import random


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AstroCode")
STATE_START = 0
STATE_LEVELS = 1
STATE_LEVEL1 = 2
STATE_LEVEL2 = 3
current_state = STATE_START

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

title_font = pygame.font.Font(None, 72)
menu_font = pygame.font.Font(None, 48)
subtitle_font = pygame.font.Font(None, 36)
level_font = pygame.font.Font(None, 36)
code_font = pygame.font.Font(None, 18)

stars = []
for _ in range(200):
    x = pygame.math.Vector2(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )
    speed = random.uniform(0.1, 0.5)
    size = random.randint(1, 3)
    stars.append((x, speed, size))

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


class Command:
    def __init__(self, cmd_type, iterations=1, nested_commands=None, rect=None):
        self.cmd_type = cmd_type
        self.iterations = iterations
        self.nested_commands = nested_commands if nested_commands is not None else []
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 210, 25)

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
            "for_loop": "For Loop"
        }
        return texts.get(self.cmd_type, "Unknown")

    def is_loop(self):
        return self.cmd_type == "for_loop"

    def draw(self, surface, x, y, width, indent=0, is_nested=False):
        self.rect = pygame.Rect(
            x + indent,
            y,
            width - indent,
            25 if not self.is_loop() else 40
        )

        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=3)

        if self.is_loop():
            self._draw_loop_header(surface)

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
        else:
            text = code_font.render(self.text, True, WHITE)
            surface.blit(text, (self.rect.x + 5, self.rect.y + 5))

        return self.rect.height

    def _draw_loop_header(self, surface):
        header_text = f"Repeat {self.iterations} times:"
        text_surf = code_font.render(header_text, True, WHITE)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))


class Level:
    def __init__(self):
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

        self.commands = {
            "move": {"color": (0, 100, 200), "text": "Move Forward"},
            "turn_left": {"color": (200, 100, 0), "text": "Turn Left"},
            "turn_right": {"color": (20, 100, 0), "text": "Turn Right"},
            "reverse": {"color": (250, 100, 0), "text": "Reverse"},
            "shoot": {"color": (250, 100, 0), "text": "Shoot"}
        }
        self._init_commands()

    def reset_level(self):
        self.__init__()

    def _init_commands(self):
        basic_commands = list(self.commands.keys())
        for cmd_type in basic_commands:
            self.code_blocks.append(Command(cmd_type))

    def shoot_bullet(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_cooldown:
            return

        self.last_shot_time = current_time

        gun_length = self.player_size * 1.5
        start_x = self.player_pos[0] + self.player_size // 2 + gun_length * math.sin(math.radians(self.player_angle))
        start_y = self.player_pos[1] + self.player_size // 2 - gun_length * math.cos(math.radians(self.player_angle))
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
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

            if not self.battlefield.collidepoint(bullet["x"], bullet["y"]):
                bullets_to_remove.append(i)
                continue

            bullet_pos = (bullet["x"], bullet["y"])
            if self.check_perimeter_collision(bullet_pos):
                self.target_health = max(0, self.target_health - DAMAGE_PER_HIT)
                bullets_to_remove.append(i)

                if self.target_health <= 0:
                    self.current_popup = "shooting"

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)

    def check_perimeter_collision(self, point):
        X, y = point
        target = self.target
        tolerance = self.bullets[0]["radius"]

        left_edge = abs(X - target.left) <= tolerance
        right_edge = abs(X - target.right) <= tolerance
        top_edge = abs(y - target.top) <= tolerance
        bottom_edge = abs(y - target.bottom) <= tolerance
        if (left_edge or right_edge) and (target.top - tolerance <= y <= target.bottom + tolerance):
            return True

        if (top_edge or bottom_edge) and (target.left - tolerance <= X <= target.right + tolerance):
            return True

        corner_radius = tolerance
        corners = [
            (target.left, target.top),
            (target.right, target.top),
            (target.left, target.bottom),
            (target.right, target.bottom)
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

        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))

        health_width = (self.target_health / TARGET_MAX_HEALTH) * bar_width
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))

        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def draw_bullets(self, surface):
        if not self.bullets:
            return
        for bullet in self.bullets:
            pygame.draw.circle(surface, ORANGE, (int(bullet["x"]), int(bullet["y"])), bullet["radius"])

    def draw_player(self, surface):
        body_rect = pygame.Rect(*self.player_pos, self.player_size, self.player_size)
        pygame.draw.rect(surface, CYAN, body_rect)

        gun_length = self.player_size * 1.5
        gun_center = (body_rect.centerx, body_rect.centery)
        end_x = gun_center[0] + gun_length * math.sin(math.radians(self.player_angle))
        end_y = gun_center[1] - gun_length * math.cos(math.radians(self.player_angle))
        pygame.draw.line(surface, ORANGE, gun_center, (end_x, end_y), 3)

    def draw_code_blocks(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.commands_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.commands_area, 2, border_radius=5)

        for i, cmd in enumerate(self.code_blocks):
            cmd.rect = pygame.Rect(60 + i * 90, 15, 90, 25)
            pygame.draw.rect(surface, cmd.color, cmd.rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, cmd.rect, 2, border_radius=3)
            text = code_font.render(cmd.text, True, WHITE)
            surface.blit(text, (cmd.rect.x + 5, cmd.rect.y + 5))

        pygame.draw.rect(surface, DARK_GRAY, self.code_area, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.code_area, 2, border_radius=5)

        y_offset = self.code_area.y + 10
        for cmd in self.main_code:
            cmd_height = cmd.draw(
                surface,
                self.code_area.x + 10,
                y_offset,
                self.code_area.width - 20
            )
            y_offset += cmd_height + 5

    def check_collision(self):
        gun_length = self.player_size * 1.5
        gun_tip_x = self.player_pos[0] + self.player_size // 2 + gun_length * math.sin(math.radians(self.player_angle))
        gun_tip_y = self.player_pos[1] + self.player_size // 2 - gun_length * math.cos(math.radians(self.player_angle))
        target_rect = self.target

        if (math.isclose(gun_tip_x, target_rect.left) or math.isclose(gun_tip_x, target_rect.right)):
            if target_rect.top <= gun_tip_y <= target_rect.bottom:
                return True
        if (math.isclose(gun_tip_y, target_rect.top) or math.isclose(gun_tip_y, target_rect.bottom)):
            if target_rect.left <= gun_tip_x <= target_rect.right:
                return True

        return False

    def in_range(self):
        gun_length = self.player_size * 1.5
        gun_tip_x = self.player_pos[0] + self.player_size // 2 + gun_length * math.sin(math.radians(self.player_angle))
        gun_tip_y = self.player_pos[1] + self.player_size // 2 - gun_length * math.cos(math.radians(self.player_angle))
        left = self.target.left
        right = self.target.right
        top = self.target.top
        bottom = self.target.bottom

        closest_x = max(left, min(gun_tip_x, right))
        closest_y = max(top, min(gun_tip_y, bottom))
        if (left <= gun_tip_x <= right) and (top <= gun_tip_y <= bottom):
            dist_left = gun_tip_x - left
            dist_right = right - gun_tip_x
            dist_top = gun_tip_y - top
            dist_bottom = bottom - gun_tip_y
            min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
            return min_dist < 40
        else:
            if closest_x == left or closest_x == right:
                dist_x = abs(gun_tip_x - closest_x)
                dist_y = abs(gun_tip_y - closest_y)
                return math.sqrt(dist_x ** 2 + dist_y ** 2) < 40
            else:
                dist_x = abs(gun_tip_x - closest_x)
                dist_y = abs(gun_tip_y - closest_y)
                return math.sqrt(dist_x ** 2 + dist_y ** 2) < 40

    def handle_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for block in self.code_blocks:
                if block.rect.collidepoint(mouse_pos):
                    self.dragging = {
                        "type": block.cmd_type,
                        "offset": (mouse_pos[0] - block.rect.x,
                                   mouse_pos[1] - block.rect.y)
                    }
                    return

            for i, cmd in enumerate(self.main_code):
                if cmd.is_loop():
                    iteration_box = self._get_iteration_box(cmd)
                    if iteration_box.collidepoint(mouse_pos):
                        self.editing_loop_index = i
                        self.editing_text = str(cmd.iterations)
                        return

            self.editing_loop_index = None

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            if self.code_area.collidepoint(mouse_pos):
                for cmd in self.main_code:
                    if cmd.is_loop() and cmd.rect.collidepoint(mouse_pos):
                        rel_y = mouse_pos[1] - cmd.rect.y

                        if True:
                            nested_index = (rel_y - 40) // 30
                            nested_index = max(0, min(nested_index, len(cmd.nested_commands)))
                            new_cmd = Command(
                                cmd_type=self.dragging["type"],
                                iterations=3 if self.dragging["type"] == "for_loop" else 1,
                                nested_commands=[] if self.dragging["type"] == "for_loop" else None,
                                rect=pygame.Rect(
                                    cmd.rect.x + 20,
                                    cmd.rect.y + 40 + nested_index * 30,
                                    160 if self.dragging["type"] != "for_loop" else 190,
                                    25 if self.dragging["type"] != "for_loop" else 40
                                )
                            )

                            cmd.nested_commands.insert(nested_index, new_cmd)
                            self.dragging = None
                            self.recalculate_code_positions()
                            return

                self.add_to_main_code(self.dragging["type"], mouse_pos)

            self.dragging = None
            self.recalculate_code_positions()

        elif event.type == pygame.KEYDOWN and self.editing_loop_index is not None:
            cmd = self.main_code[self.editing_loop_index]

            if event.key == pygame.K_RETURN:
                if self.editing_text.isdigit() and int(self.editing_text) > 0:
                    cmd.iterations = min(99, int(self.editing_text))
                self.editing_loop_index = None
            elif event.key == pygame.K_BACKSPACE:
                self.editing_text = self.editing_text[:-1]
            elif event.unicode.isdigit():
                if len(self.editing_text) < 2:
                    self.editing_text += event.unicode

        if self.run_button.is_clicked(mouse_pos, event):
            self.execute_commands()

        if self.reset_button.is_clicked(mouse_pos, event):
            self.main_code = []
            self.recalculate_code_positions()

    def _get_iteration_box(self, cmd):
        header_text = "Repeat "
        text_width = code_font.size(header_text)[0]
        return pygame.Rect(
            cmd.rect.x + 10 + text_width,
            cmd.rect.y + 5,
            40,
            20
        )

    """def execute_command(self, mouse_pos, event):
        step_delay = 500
        for cmd in self.main_code:
            if cmd["type"] == "for_loop":
                for _ in range(cmd["iterations"]):
                    for _ in cmd["nested_commands"]:
                        self.execute_command(mouse_pos, event)
            else:
                if cmd["type"] == "move":
                    dx = 40 * math.sin(math.radians(self.player_angle))
                    dy = -100 * math.cos(math.radians(self.player_angle))
                    self.player_pos[0] += dx
                    self.player_pos[1] += dy

                    self.player_pos[0] = max(self.battlefield.left,
                                             min(self.player_pos[0], self.battlefield.right - self.player_size))
                    self.player_pos[1] = max(self.battlefield.top,
                                             min(self.player_pos[1], self.battlefield.bottom - self.player_size))
                elif cmd["type"] == "turn_left":
                    self.player_angle = (self.player_angle - 90) % 360

                elif cmd["type"] == "reverse":
                    dx = 40 * math.sin(math.radians(self.player_angle))
                    dy = -40 * math.cos(math.radians(self.player_angle))
                    self.player_pos[0] -= dx
                    self.player_pos[1] -= dy

                    self.player_pos[0] = max(self.battlefield.left,
                                             min(self.player_pos[0], self.battlefield.right - self.player_size))
                    self.player_pos[1] = max(self.battlefield.top,
                                             min(self.player_pos[1], self.battlefield.bottom - self.player_size))

                elif cmd["type"] == "turn_right":
                    self.player_angle = (self.player_angle + 90) % 360

                elif cmd["type"] == "shoot":
                    self.shoot_bullet()

            pygame.time.wait(step_delay)
            screen.fill(BLACK)
            self.draw_all(screen, mouse_pos, event)
            pygame.display.update()"""



    def add_to_main_code(self, command_type, mouse_pos):
        pos_in_area = (mouse_pos[0] - self.code_area.x, mouse_pos[1] - self.code_area.y)

        insert_index = len(self.main_code)
        for i, cmd in enumerate(self.main_code):
            if mouse_pos[1] < cmd.rect.centery:
                insert_index = i
                break

        if insert_index > 0:
            prev_cmd = self.main_code[insert_index - 1]
            y_pos = prev_cmd.rect.bottom + 10
        else:
            y_pos = self.code_area.y + 110

        if command_type == "for_loop":
            new_cmd = Command(
                cmd_type="for_loop",
                iterations=3,
                nested_commands=[],
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    60
                )
            )
        else:
            new_cmd = Command(
                cmd_type=command_type,
                rect=pygame.Rect(
                    self.code_area.x + 20,
                    y_pos,
                    210,
                    25
                )
            )

        self.main_code.insert(insert_index, new_cmd)
        self.recalculate_code_positions()

    def calculate_command(self,cmd, x, width, indent=0):


        cmd.rect.x = x + indent
        cmd.rect.y = y_offset
        cmd.rect.width = width - indent
        cmd.rect.height = 25

        if cmd.is_loop():
            cmd.rect.height = 40

            for nested_cmd in cmd.nested_commands:
                nested_height = calculate_command(
                    nested_cmd,
                    x,
                    width - 20,
                    indent + 20
                )
                cmd.rect.height += nested_height
            cmd.rect.height += 5
            y_offset += 5
        else:
            y_offset += 25

        return cmd.rect.height

    def recalculate_code_positions(self):
        y_offset = self.code_area.y + 10

        for cmd in self.main_code:
            self.calculate_command(
                cmd,
                self.code_area.x + 10,
                self.code_area.width - 20
            )

    def draw_popups(self, screen, mouse_pos, event):
        pass

    def draw_all(self, screen, mouse_pos, event):
        pygame.draw.rect(screen, GRAY, self.battlefield, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.battlefield, 2, border_radius=5)
        pygame.draw.rect(screen, RED, self.target, border_radius=3)
        self.draw_player(screen)
        self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.draw_health_bar(screen)
        self.draw_bullets(screen)
        self.draw_popups(screen, mouse_pos, event)

class Level1(Level):
    def __init__(self):
        super().__init__()
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
        self.code_blocks = []
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        super()._init_commands()

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

    screen.fill(BLACK)
    draw_starfield()

    if current_state == STATE_START:
        update_starfield(dt)
        title_text = title_font.render("ASTROCODE", True, CYAN)
        title_shadow = title_font.render("ASTROCODE", True, PURPLE)
        pulse = math.sin(pygame.time.get_ticks() * 0.001) * 0.1 + 1
        scaled_title = pygame.transform.scale_by(title_text, pulse)
        scaled_shadow = pygame.transform.scale_by(title_shadow, pulse)
        scaled_rect = scaled_title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        screen.blit(scaled_shadow, (scaled_rect.x + 5, scaled_rect.y + 5))
        screen.blit(scaled_title, scaled_rect)

        subtitle_text = subtitle_font.render("A Cosmic Coding Adventure", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 70))
        screen.blit(subtitle_text, subtitle_rect)
        start_button.draw(screen)
        quit_button.draw(screen)

        version_text = subtitle_font.render("v1.0", True, (100, 100, 100))
        screen.blit(version_text, (WIDTH - 80, HEIGHT - 40))

    elif current_state == STATE_LEVELS:
        level_selector.draw(screen)

    elif current_state == STATE_LEVEL1:
        level1.draw_all(screen, mouse_pos, event)


    elif current_state == STATE_LEVEL2:
        level2.draw_all(screen, mouse_pos, event)

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
            level1.update_bullets(dt)
            if level1.level_state == 0:
                current_state = STATE_LEVELS

        elif current_state == STATE_LEVEL2:
            level2.handle_events(event, mouse_pos)
            level2.update_bullets(dt)
            if level2.level_state == 0:
                current_state = STATE_LEVELS
                level2.current_popup = " "


    pygame.display.flip()

pygame.quit()
sys.exit()