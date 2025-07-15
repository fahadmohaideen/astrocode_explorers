from levels.base_level import Level
import pygame
from orbital.entities.alien import Alien

pygame.init()
pygame.font.init()

class Level1(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 1
        self.target = Alien(60, 160, "target")

    def draw_game(self, screen, mouse_pos, event):
        self.update_camera()
        self.target.offset_pos = self.target.pos - self.camera_offset
        self.player.offset_pos = self.player.pos - self.camera_offset
        self.target.draw_player(screen)
        self.target.draw_health_bar(screen)
        self.player.draw_player(screen)
        # self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        if self.level_id >= 3:
            self.player.draw_health_bar(screen)
        #self.draw_bullets(screen)
        #self.draw_popups(screen, mouse_pos, event)