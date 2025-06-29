# Entry point for AstroCode
import pygame
import sys
import math  # For pulse effect in start screen
from levels.free_world import FreeWorld

# Import modules
from core.constants import (
    WIDTH, HEIGHT, BLACK, CYAN, PURPLE, WHITE,
    STATE_START, STATE_LEVELS, STATE_LEVEL1, STATE_LEVEL2,
    STATE_LEVEL3, STATE_LEVEL4, STATE_FREEROAM, FPS,
    fonts, screen
)
from core.utils import draw_starfield, update_starfield
from ui.button import Button
from ui.level_selector import LevelSelector
from levels.level1 import Level1
from levels.level2 import Level2
from levels.level3 import Level3
from levels.level4 import Level4


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("AstroCode")

        self.current_state = STATE_START
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize game components
        self._init_ui()
        self._init_levels()

    def _init_ui(self):
        """Initialize UI elements"""
        self.start_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50,
            "Start Game", (0, 100, 255), (0, 200, 255), fonts['menu_font']
        )
        self.level_select_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50,
            "Select Level", (0, 100, 255), (0, 200, 255), fonts['menu_font']
        )
        self.quit_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50,
            "Quit", (0, 100, 255), (0, 200, 255), fonts['menu_font']
        )

        self.level_selector = LevelSelector(fonts['menu_font'], fonts['title_font'])

    def _init_levels(self):
        """Initialize level instances"""
        self.free_world = FreeWorld()
        self.level1 = Level1(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        self.level2 = Level2(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        self.level3 = Level3(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        self.level4 = Level4(fonts['code_font'], fonts['title_font'], fonts['menu_font'])

    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            mouse_pos = pygame.mouse.get_pos()

            if self.current_state == STATE_START:
                if self.start_button.is_clicked(mouse_pos, event):
                    self.current_state = STATE_LEVELS
                if self.quit_button.is_clicked(mouse_pos, event):
                    self.running = False

            elif self.current_state == STATE_LEVELS:
                self._handle_level_selection(event, mouse_pos)

            elif self.current_state == STATE_LEVEL1:
                self._handle_level_events(self.level1, event, mouse_pos)

            elif self.current_state == STATE_LEVEL2:
                self._handle_level_events(self.level2, event, mouse_pos)

            elif self.current_state == STATE_LEVEL3:
                self._handle_level_events(self.level3, event, mouse_pos)

            elif self.current_state == STATE_LEVEL4:
                self._handle_level_events(self.level4, event, mouse_pos)

            elif self.current_state == STATE_FREEROAM:
                self.free_world.handle_event(event, mouse_pos)
                if self.free_world.exit_to_levels:
                    self.current_state = STATE_LEVELS
                    self.free_world.exit_to_levels = False

    def _handle_level_selection(self, event, mouse_pos):
        """Handle level selection logic"""
        selected_level = self.level_selector.handle_click(mouse_pos, event)
        if selected_level == 1:
            self.current_state = STATE_LEVEL1
            self.level1.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        elif selected_level == 2:
            self.current_state = STATE_LEVEL2
            self.level2.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        elif selected_level == 3:
            self.current_state = STATE_LEVEL3
            self.level3.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        elif selected_level == 4:
            self.current_state = STATE_LEVEL4
            self.level4.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
        elif selected_level == "free_roam":
            self.current_state = STATE_FREEROAM

    def _handle_level_events(self, level, event, mouse_pos):
        """Handle events for a specific level"""
        level.handle_events(event, mouse_pos)
        if level.exit_to_levels:
            self.current_state = STATE_LEVELS
            level.exit_to_levels = False

    def update(self, dt):
        """Update game state"""
        if self.current_state == STATE_FREEROAM:
            keys = pygame.key.get_pressed()
            self.free_world.update(dt, keys)

        # Update starfield for start screen
        if self.current_state == STATE_START:
            update_starfield(dt)

    def draw(self):
        """Draw everything to the screen"""
        screen.fill(BLACK)
        draw_starfield(screen)

        if self.current_state == STATE_START:
            self._draw_start_screen()
        elif self.current_state == STATE_LEVELS:
            self.level_selector.draw(screen)
        elif self.current_state == STATE_LEVEL1:
            self.level1.draw_game(screen, pygame.mouse.get_pos(), None)
            self.level1.update(self.clock.get_time() / 1000)
        elif self.current_state == STATE_LEVEL2:
            self.level2.draw_all(screen, pygame.mouse.get_pos(), None)
            self.level2.update(self.clock.get_time() / 1000)
        elif self.current_state == STATE_LEVEL3:
            self.level3.draw_all(screen, pygame.mouse.get_pos(), None)
            self.level3.update(self.clock.get_time() / 1000)
        elif self.current_state == STATE_LEVEL4:
            self.level4.draw_all(screen, pygame.mouse.get_pos(), None)
            self.level4.update(self.clock.get_time() / 1000)
        elif self.current_state == STATE_FREEROAM:
            self.free_world.draw(screen)

        pygame.display.flip()

    def _draw_start_screen(self):
        """Draw the start screen elements"""
        # Draw title with pulse effect
        title_text = fonts['title_font'].render("ASTROCODE", True, CYAN)
        title_shadow = fonts['title_font'].render("ASTROCODE", True, PURPLE)
        pulse = math.sin(pygame.time.get_ticks() * 0.001) * 0.1 + 1
        scaled_title = pygame.transform.scale_by(title_text, pulse)
        scaled_shadow = pygame.transform.scale_by(title_shadow, pulse)
        scaled_rect = scaled_title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        screen.blit(scaled_shadow, (scaled_rect.x + 5, scaled_rect.y + 5))
        screen.blit(scaled_title, scaled_rect)

        # Draw subtitle
        subtitle_text = fonts['subtitle_font'].render("A Cosmic Coding Adventure", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 70))
        screen.blit(subtitle_text, subtitle_rect)

        # Draw buttons
        self.start_button.draw(screen)
        self.quit_button.draw(screen)

        # Version info
        version_text = fonts['subtitle_font'].render("v1.0", True, (100, 100, 100))
        screen.blit(version_text, (WIDTH - 80, HEIGHT - 40))

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000  # Get delta time in seconds

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
