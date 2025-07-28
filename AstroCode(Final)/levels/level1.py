import pygame
import os
from levels.base_level import Level
from entities.alien import Alien
from core.constants import WIDTH, WHITE, GREEN, DARK_GRAY, BLUE, CYAN, HEIGHT

pygame.init()
pygame.font.init()


class Level1(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.level_id = 1
        self.enable_wasd = False
        self.total_aliens_to_eliminate = 1


        self.load_assets()


        self.aliens.clear()
        self.target_alien = Alien(WIDTH // 2 + 200, HEIGHT // 2 - 300, "Player")
        self.aliens.append(self.target_alien)
        self.curr_nearest_alien = self.target_alien


        self.code_blocks.clear()
        self.commands = {
            "move_up": {"color": (0, 100, 200), "text": "Move Up"},
            "move_left": {"color": (200, 100, 0), "text": "Move Left"},
            "move_right": {"color": (20, 100, 0), "text": "Move Right"},
            "move_down": {"color": (250, 100, 0), "text": "Move Down"},
            "shoot": {"color": (250, 100, 0), "text": "Shoot"}
        }
        super()._init_commands()

    def load_assets(self):
        try:
            ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")


            raw_tile = pygame.image.load(os.path.join(ASSETS_PATH, "tile.png"))
            self.tile_img = pygame.transform.scale(raw_tile, (self.TILE_SIZE, self.TILE_SIZE))


            self.hero_img = pygame.image.load(os.path.join(ASSETS_PATH, "hero.png"))
            self.hero_img = pygame.transform.scale(self.hero_img, (55, 55))


            self.walk_frames = [
                pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "walk1.png")), (50, 50)),
                pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "walk2.png")), (50, 50)),
                pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "walk3.png")), (50, 50))
            ]
        except Exception as e:
            print(f"Error in Level 1 asset loading: {e}")

    def update(self, dt, keys):
        self.player.update_bullets(self.aliens, self.level_id, dt)
        if self.aliens:
            target = self.aliens[0]
            if target.health <= 0 and not self.level_completed:
                self.level_completed = True
                self.current_popup = "victory"
                self.aliens_eliminated = 1

    def draw_game(self, screen, mouse_pos, event):
        self.update_camera()
        self.draw_terrain(screen)


        if self.aliens:
            target = self.aliens[0]
            try:
                ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
                target_img_path = os.path.join(ASSETS_PATH, "target.png")
                target_img = pygame.transform.scale(pygame.image.load(target_img_path).convert_alpha(), (60, 60))
                target.offset_pos = target.pos - self.camera_offset
                target.draw(surface=screen, image=target_img)
            except Exception as e:
                print(f"Error loading target.png: {e}")
                pygame.draw.circle(screen, (255, 0, 0), target.offset_pos, 30)

        self.player.offset_pos = self.player.pos - self.camera_offset
        self.player.draw_player(screen, self.walk_frames[0])
        self.run_button.draw(screen)
        self.reset_button.draw(screen)
        self.draw_bullets(screen)
        self.draw_elimination_counter(screen)
        self.draw_popups(screen, mouse_pos, event)
        self.draw_level_intro(screen)

    def draw_level_intro(self, surface):
        font = pygame.font.Font(None, 28)
        text = "Mission: Use the command blocks to destroy the target!"
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 30))
        surface.blit(text_surface, text_rect)