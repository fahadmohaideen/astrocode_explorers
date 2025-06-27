# Level 1 logic
from levels.base_level import Level
import pygame

pygame.init()
pygame.font.init()

class Level1(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 1
        # Level1 specific initialization