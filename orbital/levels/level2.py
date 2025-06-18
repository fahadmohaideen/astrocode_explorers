from levels.base_level import Level
from core.constants import FOR_LOOP_COLOR
import pygame

pygame.init()
pygame.font.init()

class Level2(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 2
        self.code_blocks = []
        self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        super()._init_commands()