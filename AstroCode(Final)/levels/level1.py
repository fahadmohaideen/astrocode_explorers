from levels.base_level import Level
import pygame
from entities.alien import Alien
from core.constants import BLUE, RED

pygame.init()
pygame.font.init()

class Level1(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 1
        self.target = Alien(60, 160, "target")

        target_image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(target_image, RED, (30, 30), 30)
        self.target.image = target_image
        player_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(player_image, BLUE, (0, 0, 50, 50))
        self.player.image = player_image

    def draw_game(self, screen, mouse_pos, event):
        self.update_camera()
        self.target.offset_pos = self.target.pos - self.camera_offset
        self.player.offset_pos = self.player.pos - self.camera_offset
        self.target.draw_player(screen, self.target.image)
        self.target.draw_health_bar(screen)
        self.player.draw_player(screen, self.player.image)
        # self.draw_code_blocks(screen)
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        if self.level_id >= 3:
            self.player.draw_health_bar(screen)
        #self.draw_bullets(screen)
        #self.draw_popups(screen, mouse_pos, event)