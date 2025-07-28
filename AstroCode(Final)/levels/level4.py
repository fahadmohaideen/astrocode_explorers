import pygame
from levels.level3 import Level3
from core.constants import WIDTH, HEIGHT, WHITE


class Level4(Level3):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        self.commands["while_loop"] = {"color": (255, 51, 153), "text": "while"}
        self.level_id = 4
        self.enable_wasd = True
        self.total_aliens_to_eliminate = 3

        for alien in self.aliens:
            alien.shielded = False

        self.show_briefing = True
        self.briefing_start_time = 0
        self.briefing_duration_ms = 8000

    def update(self, dt, keys):
        if self.player.is_dying:
            return
        if self.player.health <= 0:
            self.player.is_dying = True
            return

        self.handle_player_movement(dt, keys)

        spawn_area_width = WIDTH + 1000
        spawn_area_height = HEIGHT + 1000

        for alien in self.aliens:
            if alien.active:
                alien.update_shield()
                alien.move_randomly(dt, spawn_area_width, spawn_area_height, self.player.pos)
                alien.shoot_at_player(self.player, dt)
                alien.update_bullets(self.player, self.level_id, dt)

        active_aliens = [a for a in self.aliens if a.active]
        self.player.update_bullets(active_aliens, self.level_id, dt)

    def draw_level_intro(self, surface):
        if not self.show_briefing:
            return

        current_time = pygame.time.get_ticks()
        if self.briefing_start_time == 0:
            self.briefing_start_time = current_time

        if current_time - self.briefing_start_time > self.briefing_duration_ms:
            self.show_briefing = False
            return

        instruction = "Final Mission: The aliens are now hostile and will chase you!"
        font = pygame.font.Font(None, 28)
        text_surface = font.render(instruction, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 150))
        surface.blit(text_surface, text_rect)

    def draw_popups(self, screen, mouse_pos, event):
        super(Level3, self).draw_popups(screen, mouse_pos, event)

    def handle_events(self, event, mouse_pos):
        super(Level3, self).handle_events(event, mouse_pos)