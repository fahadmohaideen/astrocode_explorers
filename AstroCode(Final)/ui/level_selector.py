import pygame
from core.constants import WHITE, BLUE, CYAN, GREEN, WIDTH, HEIGHT, GRAY # Import necessary constants
from ui.button import Button

class LevelSelector:
    def __init__(self, menu_font, title_font, highest_level_unlocked):
        self.levels = []
        self.menu_font = menu_font
        self.title_font = title_font
        self.back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back", BLUE, CYAN, self.menu_font)
        self.highest_level_unlocked = highest_level_unlocked
        button_size = 60
        padding = 20
        start_x = WIDTH // 2 - (2 * button_size + padding)
        start_y = HEIGHT // 4

        for i in range(4):
            x = WIDTH // 2 - 150
            y = HEIGHT // 2 - 100 + (i * 60)
            self.levels.append(Button(x, y, 300, 50, f"Level {i + 1}", (0, 100, 255), (0, 200, 255), menu_font))

        self.back_button = Button(WIDTH // 2 - 75, HEIGHT - 80, 150, 40, "Back", (150, 0, 0), (255, 0, 0), menu_font)

    def draw(self, screen):
        title_text = self.title_font.render("Select a Level", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, btn in enumerate(self.levels):
            level_num = i + 1
            if level_num > self.highest_level_unlocked:
                pygame.draw.rect(screen, GRAY, btn.rect, border_radius=8) # Gray background
                text_surface = self.menu_font.render(f"Level {level_num} (Locked)", True, (100, 100, 100))  # Gray text
                screen.blit(text_surface, (btn.rect.centerx - text_surface.get_width() // 2, btn.rect.y + 10))
            else:
                btn.draw(screen)

        self.back_button.draw(screen)

    def handle_click(self, mouse_pos, event):
        for i, btn in enumerate(self.levels):
            level_num = i + 1
            if level_num <= self.highest_level_unlocked:
                if btn.is_clicked(mouse_pos, event):
                    return level_num
        if self.back_button.is_clicked(mouse_pos, event):
            return "back"
        return None