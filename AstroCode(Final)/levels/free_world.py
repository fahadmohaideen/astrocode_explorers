import pygame
import os
import math
from core.constants import WIDTH, HEIGHT, GREEN, RED, fonts
from levels.base_level import Level
from ui.button import Button



class FreeWorld:
    def __init__(self):
        self.run_button = Button(WIDTH - 200, HEIGHT - 80, 120, 50, "Run", GREEN, GREEN, fonts['menu_font'])
        self.reset_button = Button(WIDTH - 350, HEIGHT - 80, 120, 50, "Reset", RED, RED, fonts['menu_font'])
        self.clock = pygame.time.Clock()
        self.TILE_SIZE = 50
        self.hero_pos = [0, 0]  # world coordinates
        self.speed = 500
        self.panel_visible = False
        self.font = pygame.font.SysFont("consolas", 24)
        self.exit_to_levels = False

        # Load assets
        ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
        raw_tile = pygame.image.load(os.path.join(ASSETS_PATH, "tile.png"))
        self.tile_img = pygame.transform.scale(raw_tile, (self.TILE_SIZE, self.TILE_SIZE))
        self.hero_img = pygame.image.load(os.path.join(ASSETS_PATH, "hero.png"))
        self.hero_img = pygame.transform.scale(self.hero_img, (55, 55))
        self.hero_pos = [WIDTH // 2, HEIGHT // 2]  # or wherever it is initialized
        self.hero_rect = self.hero_img.get_rect(center=self.hero_pos)

    def draw_terrain(self, surface):
        cols = (WIDTH // self.TILE_SIZE) + 3
        rows = (HEIGHT // self.TILE_SIZE) + 3
        offset_x = int(self.hero_pos[0] // self.TILE_SIZE)
        offset_y = int(self.hero_pos[1] // self.TILE_SIZE)

        for i in range(-10, cols):
            for j in range(-10, rows):
                world_x = (offset_x + i) * self.TILE_SIZE
                world_y = (offset_y + j) * self.TILE_SIZE
                screen_x = world_x - self.hero_pos[0] + WIDTH // 2
                screen_y = world_y - self.hero_pos[1] + HEIGHT // 2

                if 0 - self.TILE_SIZE <= screen_x <= WIDTH and 0 - self.TILE_SIZE <= screen_y <= HEIGHT:
                    surface.blit(self.tile_img, (screen_x, screen_y))

    def draw_hero(self, surface):
        screen_x = WIDTH // 2
        screen_y = HEIGHT // 2  # <-- assign to self.hero_rect
        surface.blit(self.hero_img, self.hero_rect)

    def draw_panel(self, surface):
        panel_width = 300
        panel_height = 400
        panel_x = WIDTH - panel_width - 20
        panel_y = HEIGHT - panel_height - 20

        overlay = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        overlay.fill((30, 30, 30, 200))
        surface.blit(overlay, (panel_x, panel_y))

        pygame.draw.rect(surface, (0, 25, 25), (panel_x, panel_y, panel_width, panel_height), border_radius=8)

        title = self.font.render("Command Panel", True, (255, 255, 255))
        surface.blit(title, (panel_x + 10, panel_y + 10))

        # Optional: draw placeholder buttons or command blocks here
        sample_command = self.font.render("→ Move Forward", True, (200, 200, 200))
        surface.blit(sample_command, (panel_x + 10, panel_y + 50))


    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONUP:
            print("Mouse clicked at", mouse_pos)

            self.hero_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 40, 40)
            if self.hero_rect and self.hero_rect.collidepoint(mouse_pos):
                print("Astronaut clicked!")
                self.panel_visible = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
           self.exit_to_levels = True

    def update(self, dt, keys):
        dx = dy = 0
        if self.panel_visible:
            return
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * dt

        self.hero_pos[0] += dx
        self.hero_pos[1] += dy

    def draw(self, screen):
        self.draw_terrain(screen)
        self.draw_hero(screen)
        if self.panel_visible:
            self.draw_panel(screen)






