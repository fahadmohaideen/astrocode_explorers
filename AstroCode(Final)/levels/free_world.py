import pygame
import os
import math
import random
from core.constants import WIDTH, HEIGHT, GREEN, RED, BLUE, fonts
from ui.button import Button

# Alien types and their properties
ALIEN_TYPES = ["TypeA", "TypeB", "TypeC"]
BULLET_TYPES = {
    "TypeA": "red",
    "TypeB": "green",
    "TypeC": "blue"
}
ALIEN_COLORS = {
    "TypeA": (255, 100, 100),
    "TypeB": (100, 255, 100),
    "TypeC": (100, 100, 255)
}


class FreeWorld:
    def __init__(self):
        # Initialize game state
        self._setup_ui()
        self._setup_game_state()
        self._setup_camera()
        self._setup_command_system()
        self._setup_phases()
        self._load_assets()

    def _setup_ui(self):
        """Initialize UI elements and constants"""
        self.PANEL_COLOR = (30, 30, 30, 200)
        self.COMMAND_COLUMN_WIDTH = 200
        self.EXECUTION_COLUMN_WIDTH = 200
        self.COMMAND_BUTTON_HEIGHT = 40
        self.BUTTON_SPACING = 10

        # Game buttons
        self.run_button = Button(WIDTH - 250, HEIGHT - 100, 120, 50, "Run", GREEN, GREEN, fonts['menu_font'])
        self.reset_button = Button(WIDTH - 400, HEIGHT - 100, 120, 50, "Reset", RED, RED, fonts['menu_font'])
        self.clear_button = Button(WIDTH - 550, HEIGHT - 100, 120, 50, "Clear", BLUE, BLUE, fonts['menu_font'])

        self.font = pygame.font.SysFont("consolas", 24)
        self.panel_visible = False

    def _setup_game_state(self):
        """Initialize core game state variables"""
        self.clock = pygame.time.Clock()
        self.TILE_SIZE = 50
        self.hero_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.speed = 500
        self.exit_to_levels = False
        self.phase = 1
        self.phase_complete_message_timer = 0
        self.phase1_title_timer = 3.0  # Show for 3 seconds at start

    def _setup_camera(self):
        """Initialize camera system"""
        self.camera_offset = pygame.Vector2(0, 0)
        self.camera_active = False

    def _setup_command_system(self):
        """Initialize command system"""
        self.available_commands = ["Move Up", "Move Down", "Move Left", "Move Right"]
        self.command_queue = []
        self.dragging_command = None
        self.drag_offset = pygame.Vector2(0, 0)
        self.executing_commands = False
        self.current_command_index = 0
        self.command_execution_timer = 0
        self.command_delay = 0.5

    def _setup_phases(self):
        """Initialize phase-specific systems"""
        # Phase 2 - Alien combat
        self.aliens = []
        self.aliens_defeated = 0
        self.alien_images = {}
        self.bullet_images = {}
        self.particles = []
        self.load_alien_assets()

        # Condition system
        self.condition_being_defined = None
        self.condition_commands = []
        self.in_conditional_block = False
        self.conditional_blocks = []
        self.loop_blocks = []
        self.current_loop_iterations = {}
        self.loop_stack = []

    def _load_assets(self):
        """Load all game assets"""
        ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

        # Load tile and hero images
        raw_tile = pygame.image.load(os.path.join(ASSETS_PATH, "tile.png"))
        self.tile_img = pygame.transform.scale(raw_tile, (self.TILE_SIZE, self.TILE_SIZE))
        self.hero_img = pygame.image.load(os.path.join(ASSETS_PATH, "hero.png"))
        self.hero_img = pygame.transform.scale(self.hero_img, (55, 55))
        self.hero_rect = self.hero_img.get_rect(center=self.hero_pos)

        # Load animation frames
        self.walk_frames = [
            pygame.image.load(os.path.join(ASSETS_PATH, "walk1.png")),
            pygame.image.load(os.path.join(ASSETS_PATH, "walk2.png")),
            pygame.image.load(os.path.join(ASSETS_PATH, "walk3.png"))
        ]
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 0.1

        # Load tutorial target
        self.tutorial_target = pygame.Rect(WIDTH // 2 + 300, HEIGHT // 2 - 125, 50, 50)
        self.target_img = pygame.image.load(os.path.join(ASSETS_PATH, "target.png"))
        self.target_img = pygame.transform.scale(self.target_img, (50, 50))
        self.bullet = None
        self.bullet_speed = 600

    def load_alien_assets(self):
        """Load all alien and bullet assets for Phase 2"""
        ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

        # Load alien images
        for alien_type in ALIEN_TYPES:
            img = pygame.image.load(os.path.join(ASSETS_PATH, f"alien_{alien_type.lower()}.png")).convert_alpha()
            self.alien_images[alien_type] = pygame.transform.scale(img, (50, 50))

        # Load bullet images
        for color in ["red", "green", "blue"]:
            img = pygame.image.load(os.path.join(ASSETS_PATH, f"bullet_{color}.png")).convert_alpha()
            self.bullet_images[color] = pygame.transform.scale(img, (60, 30))

    def start_phase_2(self):
        """Initialize Phase 2 - Alien Combat"""
        print("Starting Phase 2 - Alien Combat")
        self.phase = 2
        self.hero_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.camera_active = True
        self.camera_offset = pygame.Vector2(0, 0)
        self.aliens = []
        self.aliens_defeated = 0
        self.spawn_aliens(3)  # Spawn initial aliens
        self.panel_visible = False
        self.phase_complete_message_timer = 2.0

        # Add conditional commands in Phase 2
        self.available_commands.extend([
            "If Alien Near",
            "If Alien TypeA",
            "If Alien TypeB",
            "If Alien TypeC",
            "End If"
        ])

    def spawn_aliens(self, count):
        """Spawn aliens at random positions with better distribution"""
        spawn_margin = 300  # Minimum distance from screen edges
        spawn_area_width = WIDTH + 1000
        spawn_area_height = HEIGHT + 1000

        for _ in range(count):
            alien_type = random.choice(ALIEN_TYPES)

            # Spawn in one of four quadrants around the player
            quadrant = random.randint(0, 3)
            if quadrant == 0:  # Top-right
                x = random.randint(WIDTH // 2 + 200, spawn_area_width)
                y = random.randint(100, HEIGHT // 2 - 100)
            elif quadrant == 1:  # Bottom-right
                x = random.randint(WIDTH // 2 + 200, spawn_area_width)
                y = random.randint(HEIGHT // 2 + 200, spawn_area_height)
            elif quadrant == 2:  # Top-left
                x = random.randint(100, WIDTH // 2 - 200)
                y = random.randint(100, HEIGHT // 2 - 100)
            else:  # Bottom-left
                x = random.randint(100, WIDTH // 2 - 200)
                y = random.randint(HEIGHT // 2 + 200, spawn_area_height)

            self.aliens.append({
                "type": alien_type,
                "pos": pygame.Vector2(x, y),
                "rect": pygame.Rect(x - 25, y - 25, 50, 50),
                "health": 1,
                "spawn_time": pygame.time.get_ticks()  # Track when spawned
            })

    def update_camera(self):
        """Update camera position to follow hero"""
        if self.camera_active:
            self.camera_offset.x = self.hero_pos.x - WIDTH // 2
            self.camera_offset.y = self.hero_pos.y - HEIGHT // 2

    def draw_terrain(self, surface):
        """Draw tiled background with camera offset"""
        for x in range(-self.TILE_SIZE, WIDTH + self.TILE_SIZE, self.TILE_SIZE):
            for y in range(-self.TILE_SIZE, HEIGHT + self.TILE_SIZE, self.TILE_SIZE):
                surface.blit(self.tile_img,
                             (x - self.camera_offset.x % self.TILE_SIZE,
                              y - self.camera_offset.y % self.TILE_SIZE))

    def draw_hero(self, surface):
        """Draw hero with walking animation"""
        hero_screen_pos = self.hero_pos - self.camera_offset
        current_img = pygame.transform.scale(self.walk_frames[self.current_frame], (55, 55))
        self.hero_rect = current_img.get_rect(center=hero_screen_pos)
        surface.blit(current_img, self.hero_rect)

    def draw_aliens(self, surface):
        """Draw all aliens with type indicators and spawn markers"""
        for alien in self.aliens:
            alien_screen_pos = alien["pos"] - self.camera_offset

            # Draw direction indicator if off-screen
            if not (-100 < alien_screen_pos.x < WIDTH + 100 and
                    -100 < alien_screen_pos.y < HEIGHT + 100):
                # Calculate direction to alien
                dir_vec = (alien["pos"] - self.hero_pos).normalize()
                indicator_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2) + dir_vec * 200

                # Draw arrow pointing to alien
                pygame.draw.circle(surface, ALIEN_COLORS[alien["type"]],
                                   (int(indicator_pos.x), int(indicator_pos.y)), 10)
                pygame.draw.line(surface, ALIEN_COLORS[alien["type"]],
                                 (WIDTH // 2, HEIGHT // 2),
                                 (indicator_pos.x, indicator_pos.y), 2)
                continue

            # Draw alien image
            surface.blit(self.alien_images[alien["type"]],
                         (alien_screen_pos.x - 25,
                          alien_screen_pos.y - 25))

            # Draw health bar
            pygame.draw.rect(surface, (255, 0, 0),
                             (alien_screen_pos.x - 25, alien_screen_pos.y - 35, 50, 5))
            pygame.draw.rect(surface, (0, 255, 0),
                             (alien_screen_pos.x - 25, alien_screen_pos.y - 35,
                              50 * alien["health"], 5))

            # Draw spawn effect for new aliens
            if pygame.time.get_ticks() - alien["spawn_time"] < 1000:
                alpha = min(255, (pygame.time.get_ticks() - alien["spawn_time"]) // 4)
                size = 50 + (pygame.time.get_ticks() - alien["spawn_time"]) // 20
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*ALIEN_COLORS[alien["type"]], alpha),
                                   (size, size), size)
                surface.blit(s, (alien_screen_pos.x - size, alien_screen_pos.y - size))

    def draw(self, screen):
        """Draw all game objects with debug info"""
        # ... (previous draw code remains the same until after particle drawing)

        # Draw debug info (optional)
        if self.phase == 2:
            debug_text = self.font.render(f"Aliens: {len(self.aliens)} (Defeated: {self.aliens_defeated})",
                                          True, (255, 255, 255))
            screen.blit(debug_text, (10, 10))

            # Draw minimap
            map_size = 150
            map_pos = (WIDTH - map_size - 10, 10)
            pygame.draw.rect(screen, (50, 50, 50), (*map_pos, map_size, map_size))

            # Draw hero on minimap
            hero_map_x = map_pos[0] + (self.hero_pos.x / (WIDTH + 1000)) * map_size
            hero_map_y = map_pos[1] + (self.hero_pos.y / (HEIGHT + 1000)) * map_size
            pygame.draw.circle(screen, (0, 255, 0), (int(hero_map_x), int(hero_map_y)), 5)

            # Draw aliens on minimap
            for alien in self.aliens:
                alien_map_x = map_pos[0] + (alien["pos"].x / (WIDTH + 1000)) * map_size
                alien_map_y = map_pos[1] + (alien["pos"].y / (HEIGHT + 1000)) * map_size
                pygame.draw.circle(screen, ALIEN_COLORS[alien["type"]],
                                   (int(alien_map_x), int(alien_map_y)), 3)

    def draw_panel(self, surface):
        """Draw full-screen command panel"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.PANEL_COLOR)
        surface.blit(overlay, (0, 0))
        self.draw_command_column(surface)
        self.draw_execution_column(surface)

        # Draw Run/Reset/Clear buttons only when panel is visible
        self.run_button.draw(surface)
        self.reset_button.draw(surface)
        self.clear_button.draw(surface)

    def draw_command_column(self, surface):
        """Draw available commands column"""
        title = self.font.render("Available Commands", True, (255, 255, 255))
        surface.blit(title, (50, 50))

        # Basic movement commands (only in Phase 1)
        if self.phase == 1:
            basic_commands = ["Move Up", "Move Down", "Move Left", "Move Right"]
            for i, cmd in enumerate(basic_commands):
                btn_rect = pygame.Rect(50, 100 + i * (self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING),
                                       self.COMMAND_COLUMN_WIDTH, self.COMMAND_BUTTON_HEIGHT)
                pygame.draw.rect(surface, GREEN, btn_rect, border_radius=4)
                text = self.font.render(cmd, True, (255, 255, 255))
                surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

        # Phase-specific commands
        if self.phase == 1:
            # Phase 1 - Basic Shoot command
            start_y = 100 + len(["Move Up", "Move Down", "Move Left", "Move Right"]) * (
                        self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING)
            btn_rect = pygame.Rect(50, start_y,
                                   self.COMMAND_COLUMN_WIDTH, self.COMMAND_BUTTON_HEIGHT)
            pygame.draw.rect(surface, RED, btn_rect, border_radius=4)
            text = self.font.render("Shoot", True, (255, 255, 255))
            surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))
        elif self.phase == 2:
            start_y = 100  # Start at the top since we're not showing move commands

            # Phase 2 - Alien-specific Shoot commands
            for i, alien_type in enumerate(ALIEN_TYPES):
                btn_rect = pygame.Rect(50, start_y + i * (self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING),
                                       self.COMMAND_COLUMN_WIDTH, self.COMMAND_BUTTON_HEIGHT)
                pygame.draw.rect(surface, ALIEN_COLORS[alien_type], btn_rect, border_radius=4)
                text = self.font.render(f"Shoot {alien_type}", True, (255, 255, 255))
                surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

            # Conditional commands (Phase 2 only)
            conditional_commands = ["If Alien Near", "If Alien TypeA", "If Alien TypeB", "If Alien TypeC", "End If"]
            for i, cmd in enumerate(conditional_commands):
                btn_rect = pygame.Rect(50, start_y + (len(ALIEN_TYPES) + i) * (
                            self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING),
                                       self.COMMAND_COLUMN_WIDTH, self.COMMAND_BUTTON_HEIGHT)
                color = (200, 200, 0)  # Yellow for conditionals
                pygame.draw.rect(surface, color, btn_rect, border_radius=4)
                text = self.font.render(cmd, True, (255, 255, 255))
                surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

        elif self.phase == 3:
            # Loop commands (yellow)
            loop_commands = ["For 3 Times", "For 5 Times", "End For"]
            # ADD MOVEMENT AND SHOOTING COMMANDS
            basic_commands = ["Move Up", "Move Down", "Move Left", "Move Right", "Shoot TypeA"]

            # Draw all commands
            all_commands = basic_commands + loop_commands
            for i, cmd in enumerate(all_commands):
                color = (200, 200, 0) if cmd in loop_commands else GREEN
                btn_rect = pygame.Rect(50, 100 + i * (self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING),
                                       self.COMMAND_COLUMN_WIDTH, self.COMMAND_BUTTON_HEIGHT)
                pygame.draw.rect(surface, color, btn_rect, border_radius=4)
                text = self.font.render(cmd, True, (255, 255, 255))
                surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

    def draw_execution_column(self, surface):
        """Draw command queue column"""
        title = self.font.render("Command Queue", True, (255, 255, 255))
        surface.blit(title, (WIDTH - self.EXECUTION_COLUMN_WIDTH - 50, 50))

        for i, cmd in enumerate(self.command_queue):
            # Color code based on command type
            if "Shoot" in cmd:
                alien_type = cmd.split()[-1]
                color = ALIEN_COLORS.get(alien_type, RED)
            elif cmd.startswith("If "):
                color = (200, 200, 0)  # Yellow for conditionals
            elif cmd == "End If":
                color = (200, 100, 0)  # Darker yellow for End If
            else:
                color = BLUE if i == self.current_command_index and self.executing_commands else GREEN

            btn_rect = pygame.Rect(WIDTH - self.EXECUTION_COLUMN_WIDTH - 50,
                                   100 + i * (self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING),
                                   self.EXECUTION_COLUMN_WIDTH, self.COMMAND_BUTTON_HEIGHT)
            pygame.draw.rect(surface, color, btn_rect, border_radius=4)
            text = self.font.render(cmd, True, (255, 255, 255))
            surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

    def handle_event(self, event, mouse_pos):
        """Handle all game events"""
        if event.type == pygame.MOUSEBUTTONUP:
            if self.hero_rect.collidepoint(mouse_pos) and not self.panel_visible:
                self.panel_visible = True

            if self.panel_visible and event.button == 1:
                self.handle_command_drop(mouse_pos)
                self.dragging_command = None

        elif event.type == pygame.MOUSEBUTTONDOWN and self.panel_visible:
            if event.button == 1:
                self.handle_command_pickup(mouse_pos)

        elif event.type == pygame.MOUSEMOTION and self.dragging_command:
            self.dragging_command["pos"] = pygame.Vector2(mouse_pos) - self.drag_offset

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.exit_to_levels = True

        # Handle Run/Reset/Clear buttons only when panel is visible
        if self.panel_visible:
            if self.run_button.is_clicked(mouse_pos, event) and not self.executing_commands:
                self.start_command_execution()
            if self.reset_button.is_clicked(mouse_pos, event):
                self.reset_game_state()
            if self.clear_button.is_clicked(mouse_pos, event):
                self.command_queue = []
                self.conditional_blocks = []

    def handle_command_pickup(self, mouse_pos):
        """Handle picking up commands from panel with proper phase support"""
        # Calculate the y-position where commands start
        start_y = 100
        button_height = self.COMMAND_BUTTON_HEIGHT
        spacing = self.BUTTON_SPACING

        # Check if click is in the command column
        command_col_rect = pygame.Rect(50, start_y,
                                       self.COMMAND_COLUMN_WIDTH,
                                       HEIGHT - start_y - 50)
        if not command_col_rect.collidepoint(mouse_pos):
            return

        # Calculate which command button was clicked based on y-position
        relative_y = mouse_pos[1] - start_y
        button_index = int(relative_y // (button_height + spacing))

        # Phase 1 commands (Basic movement + shoot)
        if self.phase == 1:
            commands = ["Move Up", "Move Down", "Move Left", "Move Right", "Shoot"]
            if 0 <= button_index < len(commands):
                self.dragging_command = {
                    "command": commands[button_index],
                    "pos": pygame.Vector2(mouse_pos)
                }
                self.drag_offset = pygame.Vector2(10, 10)

        # Phase 2 commands (Shoot types + conditionals)
        elif self.phase == 2:
            # Shoot commands come first
            shoot_commands = [f"Shoot {t}" for t in ALIEN_TYPES]
            if button_index < len(shoot_commands):
                self.dragging_command = {
                    "command": shoot_commands[button_index],
                    "pos": pygame.Vector2(mouse_pos)
                }
                self.drag_offset = pygame.Vector2(10, 10)
            else:
                # Conditionals come after shoot commands
                conditional_commands = [
                    "If Alien Near",
                    "If Alien TypeA",
                    "If Alien TypeB",
                    "If Alien TypeC",
                    "End If"
                ]
                conditional_index = button_index - len(shoot_commands)
                if 0 <= conditional_index < len(conditional_commands):
                    self.dragging_command = {
                        "command": conditional_commands[conditional_index],
                        "pos": pygame.Vector2(mouse_pos)
                    }
                    self.drag_offset = pygame.Vector2(10, 10)

        # Phase 3 commands (Movement + shooting + loops)
        elif self.phase == 3:
            commands = [
                "Move Up", "Move Down", "Move Left", "Move Right",
                "Shoot TypeA",  # Only TypeA in Phase 3
                "For 3 Times", "For 5 Times", "End For"
            ]
            if 0 <= button_index < len(commands):
                self.dragging_command = {
                    "command": commands[button_index],
                    "pos": pygame.Vector2(mouse_pos)
                }
                self.drag_offset = pygame.Vector2(10, 10)

    def handle_command_drop(self, mouse_pos):
        execution_col_rect = pygame.Rect(WIDTH - self.EXECUTION_COLUMN_WIDTH - 50, 100,
                                         self.EXECUTION_COLUMN_WIDTH, HEIGHT - 200)
        if (execution_col_rect.collidepoint(mouse_pos) and self.dragging_command):
            if self.phase == 3 and len(self.command_queue) >= 4:
                return  # Don't allow more than 4 commands in phase 3
            index = min(len(self.command_queue),
                        max(0, (mouse_pos[1] - 100) // (self.COMMAND_BUTTON_HEIGHT + self.BUTTON_SPACING)))
            self.command_queue.insert(index, self.dragging_command["command"])

    def parse_loops(self):
        """Scan the command queue to identify loop blocks with proper nesting"""
        self.loop_blocks = []
        stack = []

        for i, cmd in enumerate(self.command_queue):
            if cmd.startswith("For "):
                iterations = int(cmd.split()[1])
                stack.append({
                    'start': i,
                    'end': -1,  # Will be set when we find End For
                    'max_iterations': iterations,
                    'current_iterations': 0,
                    'nesting_level': len(stack)  # Track nesting depth
                })
            elif cmd == "End For" and stack:
                loop = stack.pop()
                loop['end'] = i
                self.loop_blocks.append(loop)

        # Clear any malformed loops (unmatched start/end)
        if stack:
            print("Warning: Unmatched For loops in command queue")

    # (start, end, iterations)

    def start_command_execution(self):
        """Start executing the command queue"""
        if self.command_queue:
            # Reset all loop states
            for loop in self.loop_blocks:
                loop['current_iterations'] = 0
                loop['active'] = False

            self.parse_conditional_blocks()
            self.parse_loops()  # Re-parse to ensure fresh state
            self.executing_commands = True
            self.current_command_index = 0
            self.command_execution_timer = 0
            self.panel_visible = False

    def parse_conditional_blocks(self):
        """Parse the command queue to identify conditional blocks"""
        self.conditional_blocks = []
        stack = []

        for i, cmd in enumerate(self.command_queue):
            if cmd.startswith("If "):
                stack.append((cmd, i))  # Store the condition and its index
            elif cmd == "End If" and stack:
                condition, start_index = stack.pop()
                # Only add if this End If matches the most recent If
                if not stack:  # Only top-level conditionals for now
                    self.conditional_blocks.append((condition, start_index, i))

    def check_condition(self, condition):
        """Check if a condition is met"""
        if condition == "If Alien Near":
            # Check if any alien is within 200 pixels
            for alien in self.aliens:
                alien_screen_pos = alien["pos"] - self.camera_offset
                if (-100 < alien_screen_pos.x < WIDTH + 100 and
                        -100 < alien_screen_pos.y < HEIGHT + 100):
                    if (alien["pos"] - self.hero_pos).length() < 200:
                        return True
            return False
        elif condition == "If Alien TypeA":
            # Check if any visible alien is TypeA
            for alien in self.aliens:
                alien_screen_pos = alien["pos"] - self.camera_offset
                if (-100 < alien_screen_pos.x < WIDTH + 100 and
                        -100 < alien_screen_pos.y < HEIGHT + 100):
                    if alien["type"] == "TypeA":
                        return True
            return False
        elif condition == "If Alien TypeB":
            # Check if any visible alien is TypeB
            for alien in self.aliens:
                alien_screen_pos = alien["pos"] - self.camera_offset
                if (-100 < alien_screen_pos.x < WIDTH + 100 and
                        -100 < alien_screen_pos.y < HEIGHT + 100):
                    if alien["type"] == "TypeB":
                        return True
            return False
        elif condition == "If Alien TypeC":
            # Check if any visible alien is TypeC
            for alien in self.aliens:
                alien_screen_pos = alien["pos"] - self.camera_offset
                if (-100 < alien_screen_pos.x < WIDTH + 100 and
                        -100 < alien_screen_pos.y < HEIGHT + 100):
                    if alien["type"] == "TypeC":
                        return True
            return False
        return False

    def execute_current_command(self):
        if self.current_command_index >= len(self.command_queue):
            self.executing_commands = False
            return

        cmd = self.command_queue[self.current_command_index]

        # Handle loop starts
        if cmd.startswith("For "):
            for loop in self.loop_blocks:
                if loop['start'] == self.current_command_index:
                    if loop['current_iterations'] < loop['max_iterations']:
                        loop['active'] = True
                        loop['current_iterations'] += 1
                        self.current_command_index += 1  # Move to first command inside loop
                    else:
                        loop['active'] = False
                        loop['current_iterations'] = 0
                        self.current_command_index = loop['end'] + 1  # Skip past loop
                    return

        # Handle loop ends
        elif cmd == "End For":
            for loop in self.loop_blocks:
                if loop['end'] == self.current_command_index and loop['active']:
                    if loop['current_iterations'] < loop['max_iterations']:
                        self.current_command_index = loop['start']  # Jump back to start
                    else:
                        loop['active'] = False
                        self.current_command_index += 1  # Continue after loop
                    return
            # If we get here, it's an unmatched End For
            self.current_command_index += 1
            return

        # Handle conditional blocks
        for condition, start, end in self.conditional_blocks:
            if self.current_command_index == start:  # This is an If command
                condition_met = self.check_condition(condition)
                if not condition_met:
                    # Skip to End If
                    self.current_command_index = end + 1
                    return
                else:
                    # Continue with next command
                    self.current_command_index += 1
                    return
            elif self.current_command_index == end:  # This is End If
                # Just continue to next command
                self.current_command_index += 1
                return

        # Execute normal commands
        if cmd == "Move Up":
            self.hero_pos.y -= 50
        elif cmd == "Move Down":
            self.hero_pos.y += 50
        elif cmd == "Move Left":
            self.hero_pos.x -= 50
        elif cmd == "Move Right":
            self.hero_pos.x += 50
        elif cmd == "Shoot" and self.bullet is None:
            self.fire_bullet()
        elif cmd.startswith("Shoot") and self.phase >= 2 and self.bullet is None:
            alien_type = cmd.split()[-1]
            self.fire_bullet(alien_type)

        # Only advance if we're not in an active loop
        if not any(loop['active'] and loop['start'] <= self.current_command_index <= loop['end']
                   for loop in self.loop_blocks):
            self.current_command_index += 1

    def fire_bullet(self, alien_type=None):
        """Fire a bullet of the appropriate type"""
        if self.bullet is None:
            # For Phase 1 or when no specific alien type is given
            if alien_type is None or self.phase == 1:
                self.bullet = {
                    "pos": pygame.Vector2(self.hero_pos.x, self.hero_pos.y),
                    "dir": pygame.Vector2(1, 0),  # Default right direction
                    "type": "red"  # Default bullet color
                }
            # For Phase 2 with specific alien type
            elif alien_type in BULLET_TYPES:
                self.bullet = {
                    "pos": pygame.Vector2(self.hero_pos.x, self.hero_pos.y),
                    "dir": pygame.Vector2(1, 0),  # Default right direction
                    "type": BULLET_TYPES[alien_type]
                }

    def update_bullet(self, dt):
        """Update bullet position and handle all collision logic"""
        if self.bullet:
            # Update bullet position
            self.bullet["pos"] += self.bullet["dir"] * self.bullet_speed * dt

            # Check wall collisions
            if not (0 <= self.bullet["pos"].x <= WIDTH + 1000 and
                    0 <= self.bullet["pos"].y <= HEIGHT + 1000):
                self.bullet = None
                return

            # Phase-specific collision handling
            if self.phase == 1:
                self._handle_phase1_collision()
            elif self.phase == 2:
                self._handle_phase2_collision()
            elif self.phase == 3:
                self._handle_phase3_collision()

    def _handle_phase1_collision(self):
        """Phase 1: Single target hit"""
        bullet_rect = pygame.Rect(
            int(self.bullet["pos"].x) - 15,
            int(self.bullet["pos"].y) - 7,
            30, 15
        )
        world_target = pygame.Rect(
            self.tutorial_target.x + self.camera_offset.x,
            self.tutorial_target.y + self.camera_offset.y,
            self.tutorial_target.width,
            self.tutorial_target.height
        )
        if bullet_rect.colliderect(world_target):
            self.complete_phase_1()
            self.bullet = None

    def _handle_phase2_collision(self):
        """Phase 2: Alien combat with types"""
        bullet_rect = pygame.Rect(
            int(self.bullet["pos"].x) - 15,
            int(self.bullet["pos"].y) - 7,
            30, 15
        )

        for alien in self.aliens[:]:  # Iterate over a copy
            if bullet_rect.colliderect(alien["rect"]):
                if self.bullet["type"] == BULLET_TYPES[alien["type"]]:
                    alien["health"] -= 1
                    if alien["health"] <= 0:
                        self.aliens.remove(alien)
                        self.aliens_defeated += 1
                        self.create_impact_particles(alien["pos"])

                        # Phase completion check - only complete when exactly 3 aliens are defeated
                        if self.aliens_defeated == 3:
                            self.start_phase_3()
                self.bullet = None
                break

    def _handle_phase3_collision(self):
        """Phase 3: Loop challenge with multi-hit aliens"""
        bullet_rect = pygame.Rect(
            int(self.bullet["pos"].x) - 15,
            int(self.bullet["pos"].y) - 7,
            30, 15
        )

        for alien in self.aliens[:]:
            if bullet_rect.colliderect(alien["rect"]):
                # In Phase 3, all aliens are TypeA
                if self.bullet["type"] == BULLET_TYPES["TypeA"]:
                    alien["health"] -= 1

                    # Create hit effect regardless of health
                    self.create_impact_particles(alien["pos"])

                    if alien["health"] <= 0:
                        self.aliens.remove(alien)

                        # Phase completion check
                        if not self.aliens:  # All aliens defeated
                            self.show_message(
                                "Mission Complete!\n"
                                "You mastered loops!"
                            )
                            # Transition to next phase or menu
                            self.phase_complete_message_timer = 3.0

                self.bullet = None
                break

    def create_impact_particles(self, pos):
        """Create explosion particles at impact position"""
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                "pos": pygame.Vector2(pos),
                "velocity": pygame.Vector2(math.cos(angle), math.sin(angle)) * speed,
                "size": random.randint(2, 5),
                "life": random.uniform(0.5, 1.0),
                "color": (random.randint(200, 255), random.randint(100, 200), random.randint(0, 100))
            })

    def update_particles(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle["pos"] += particle["velocity"] * dt
            particle["life"] -= dt
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            alpha = int(255 * (particle["life"] / 1.0))
            size = int(particle["size"] * particle["life"])
            if size > 0:
                pos = particle["pos"] - self.camera_offset
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*particle["color"], alpha), (size, size), size)
                surface.blit(s, (pos.x - size, pos.y - size))

    def complete_phase_1(self):
        """Complete Phase 1 and start Phase 2"""
        print("Tutorial completed! Starting Phase 2")
        self.phase = 2
        self.bullet = None
        self.hero_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.camera_active = True
        self.camera_offset = pygame.Vector2(0, 0)
        self.panel_visible = False
        self.phase_complete_message_timer = 2
        self.start_phase_2()

    def start_phase_3(self):
        """Initialize Phase 3 - Loop Challenges"""
        print("Starting Phase 3 - Loops")
        self.phase = 3
        self.hero_pos = pygame.Vector2(WIDTH // 4, HEIGHT // 2)

        # Create a grid of 9 aliens (3x3) with 3 health each
        self.aliens = []
        grid_positions = [(WIDTH // 2 + x * 150, HEIGHT // 2 + y * 150)
                          for x in range(3) for y in range(3)]

        for x, y in grid_positions:
            self.aliens.append({
                "type": "TypeA",
                "pos": pygame.Vector2(x, y),
                "rect": pygame.Rect(x - 25, y - 25, 50, 50),
                "health": 3,  # Each alien requires 3 hits
                "spawn_time": pygame.time.get_ticks()
            })

        # Tutorial message
        self.show_message(
            "PHASE 3: Use loops to destroy all aliens!\n"
            "Each alien requires 3 hits to defeat.\n"
            "You can only use 4 commands!"
        )

    def show_message(self, text):
        """Helper to display multi-line messages"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 30))
            pygame.display.get_surface().blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)  # Show for 3 seconds

    def reset_game_state(self):
        """Reset all game state"""
        self.phase = 1
        self.hero_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.bullet = None
        self.panel_visible = False
        self.phase_complete_message_timer = 0
        self.phase1_title_timer = 3.0
        self.command_queue = []
        self.executing_commands = False
        self.current_command_index = 0
        self.camera_active = False
        self.camera_offset = pygame.Vector2(0, 0)
        self.aliens = []
        self.aliens_defeated = 0
        self.particles = []
        self.conditional_blocks = []
        self.loop_blocks = []  # Reset loop blocks



    def update(self, dt, keys):
        """Update all game state"""
        self.update_camera()
        self.update_bullet(dt)
        self.update_particles(dt)

        # Command execution
        if self.executing_commands:
            self.command_execution_timer += dt
            if self.command_execution_timer >= self.command_delay:
                self.execute_current_command()
                self.command_execution_timer = 0
            return  # Skip other movement during command execution

        # Phase 1: Only allow movement through commands (disable WASD)
        if self.phase == 1:
            # Skip movement controls entirely in Phase 1
            # Only update animation if we're executing commands
            if self.executing_commands:
                self.frame_timer += dt
                if self.frame_timer >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                    self.frame_timer = 0
            else:
                self.current_frame = 0
        else:
            # Phase 2: Allow WASD movement
            # Movement controls
            movement = pygame.Vector2(0, 0)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                movement.x -= self.speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                movement.x += self.speed * dt
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                movement.y -= self.speed * dt
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                movement.y += self.speed * dt

            self.hero_pos += movement

            # Animation
            if movement.length() > 0:
                self.frame_timer += dt
                if self.frame_timer >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                    self.frame_timer = 0
            else:
                self.current_frame = 0

        # Phase 2: Maintain alien count
        if self.phase == 2:
            if len(self.aliens) < 3:  # Keep 3 aliens active
                self.spawn_aliens(3 - len(self.aliens))

        # Timers
        if self.phase_complete_message_timer > 0:
            self.phase_complete_message_timer -= dt
        if self.phase == 1 and self.phase1_title_timer > 0 and not self.panel_visible:
            self.phase1_title_timer -= dt

    def draw(self, screen):
        """Draw all game objects"""
        screen.fill((0, 0, 0))
        self.draw_terrain(screen)

        # Draw phase-specific elements
        if self.phase == 1:
            self._draw_phase1_elements(screen)
        if self.phase >= 2:
            self._draw_phase2_elements(screen)

        # Draw common elements
        self.draw_particles(screen)
        self.draw_hero(screen)
        self._draw_bullet(screen)

        # Draw UI elements
        if self.panel_visible:
            self.draw_panel(screen)

        self._draw_messages(screen)
        self._draw_debug_info(screen)

        if self.dragging_command:
            self._draw_dragging_command(screen)

    def _draw_phase1_elements(self, screen):
        """Draw elements specific to phase 1"""
        target_pos = pygame.Rect(
            self.tutorial_target.x - self.camera_offset.x,
            self.tutorial_target.y - self.camera_offset.y,
            self.tutorial_target.width,
            self.tutorial_target.height
        )
        screen.blit(self.target_img, target_pos)

        if self.phase1_title_timer > 0 and not self.panel_visible:
            title = self.font.render("Phase 1: Basic Commands", True, (255, 255, 255))
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            subtitle = self.font.render("Click on the hero to open command panel", True, (200, 200, 200))
            subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)

    def _draw_phase2_elements(self, screen):
        """Draw elements specific to phase 2+"""
        self.draw_aliens(screen)

        if self.phase == 3:
            # Phase 3 specific elements
            remaining = 4 - len(self.command_queue)
            counter = self.font.render(f"Commands left: {remaining}", True, (255, 255, 0))
            screen.blit(counter, (WIDTH - 260, HEIGHT - 40))

            for alien in self.aliens:
                pos = alien["pos"] - self.camera_offset
                health = self.font.render(str(alien["health"]), True, (255, 0, 0))
                screen.blit(health, (pos.x - 10, pos.y - 40))

    def _draw_bullet(self, screen):
        """Draw the bullet if it exists"""
        if self.bullet:
            bullet_pos = self.bullet["pos"] - self.camera_offset
            if self.bullet["type"] in self.bullet_images:
                bullet_img = self.bullet_images[self.bullet["type"]]
                angle = math.degrees(math.atan2(self.bullet["dir"].y, self.bullet["dir"].x))
                rotated_bullet = pygame.transform.rotate(bullet_img, -angle)
                screen.blit(rotated_bullet, (
                    bullet_pos.x - rotated_bullet.get_width() // 2,
                    bullet_pos.y - rotated_bullet.get_height() // 2
                ))

    def _draw_messages(self, screen):
        """Draw phase completion messages"""
        if self.phase_complete_message_timer > 0:
            if self.phase == 1:
                message = "Phase 1 Complete!"
            elif self.phase == 2:
                message = "Phase 2 Complete! WASD movement unlocked!"
            elif self.phase == 3:
                message = "Phase 3 Complete! Loops mastered!"
            else:
                message = "All Phases Complete!"

            text = self.font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

    def _draw_debug_info(self, screen):
        """Draw debug information when appropriate"""
        if self.phase == 2 and not self.panel_visible:
            debug_text = self.font.render(
                f"Aliens: {len(self.aliens)} (Defeated: {self.aliens_defeated})",
                True, (255, 255, 255)
            )
            screen.blit(debug_text, (10, 10))

            # Draw minimap
            map_size = 150
            map_pos = (WIDTH - map_size - 10, 10)
            pygame.draw.rect(screen, (50, 50, 50), (*map_pos, map_size, map_size))

            # Draw hero on minimap
            hero_map_x = map_pos[0] + (self.hero_pos.x / (WIDTH + 1000)) * map_size
            hero_map_y = map_pos[1] + (self.hero_pos.y / (HEIGHT + 1000)) * map_size
            pygame.draw.circle(screen, (0, 255, 0), (int(hero_map_x), int(hero_map_y)), 5)

            # Draw aliens on minimap
            for alien in self.aliens:
                alien_map_x = map_pos[0] + (alien["pos"].x / (WIDTH + 1000)) * map_size
                alien_map_y = map_pos[1] + (alien["pos"].y / (HEIGHT + 1000)) * map_size
                pygame.draw.circle(screen, ALIEN_COLORS[alien["type"]],
                                   (int(alien_map_x), int(alien_map_y)), 3)

    def _draw_dragging_command(self, screen):
        """Draw the command being dragged"""
        btn_rect = pygame.Rect(
            self.dragging_command["pos"].x,
            self.dragging_command["pos"].y,
            self.COMMAND_COLUMN_WIDTH,
            self.COMMAND_BUTTON_HEIGHT
        )
        pygame.draw.rect(screen, (100, 100, 100), btn_rect, border_radius=4)
        text = self.font.render(self.dragging_command["command"], True, (255, 255, 255))
        screen.blit(text, (btn_rect.x + 10, btn_rect.y + 10))






