
from levels.level3 import Level3
import pygame
from core.constants import FOR_LOOP_COLOR


pygame.init()
pygame.font.init()

class Level4(Level3):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 4
        self.code_font = code_font
        self.title_font = title_font
        self.code_blocks = []
        self.commands["while_loop"] = {"color": FOR_LOOP_COLOR, "text": "while"}
        super()._init_commands()