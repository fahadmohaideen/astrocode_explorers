import pygame
from core.constants import WHITE, BLUE, CYAN, GREEN, WIDTH, HEIGHT 
from ui.button import Button

class LevelSelector:
    def __init__(self, menu_font, title_font):
        self.levels = []
        self.menu_font = menu_font
        self.title_font = title_font
        self.back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back", BLUE, CYAN, self.menu_font)
        button_size = 60
        padding = 20
        start_x = WIDTH // 2 - (2 * button_size + padding)
        start_y = HEIGHT // 4

        for i in range(10):
            row = i // 5
            col = i % 5
            x = start_x + col * (button_size + padding)
            y = start_y + row * (button_size + padding)
            btn = Button(x, y, button_size, button_size, str(i + 1), BLUE, GREEN, self.menu_font)
            self.levels.append(btn)

    def draw(self, surface):
        title_text = self.title_font.render("Select Level", True, CYAN)
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
            return "back"

        return None