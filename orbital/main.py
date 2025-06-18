
import pygame
import sys
import time
import math 


from core.constants import (
    WIDTH, HEIGHT, BLACK, CYAN, PURPLE, WHITE, DARK_GRAY,
    STATE_START, STATE_LEVELS, STATE_LEVEL1, STATE_LEVEL2, STATE_LEVEL3, STATE_LEVEL4, FPS,
    TITLE_FONT_SIZE, MENU_FONT_SIZE, SUBTITLE_FONT_SIZE, CODE_FONT_SIZE, fonts, screen
)
from core.utils import draw_starfield, update_starfield
from ui.button import Button
from ui.level_selector import LevelSelector
from levels.level1 import Level1
from levels.level2 import Level2
from levels.level3 import Level3
from levels.level4 import Level4


pygame.init()
pygame.font.init() 

pygame.display.set_caption("AstroCode")

current_state = STATE_START

start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Start Game", (0, 100, 255), (0, 200, 255), fonts['menu_font'])
level_select_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50, "Select Level", (0, 100, 255), (0, 200, 255), fonts['menu_font'])
quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Quit", (0, 100, 255), (0, 200, 255), fonts['menu_font'])

level_selector = LevelSelector(fonts['menu_font'], fonts['title_font'])

level1 = Level1(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
level2 = Level2(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
level3 = Level3(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
level4 = Level4(fonts['code_font'], fonts['title_font'], fonts['menu_font'])

clock = pygame.time.Clock()
running = True
prev_time = time.time()
x = 0

while running:
    mouse_pos = pygame.mouse.get_pos()
    current_time = time.time()
    dt = (current_time - prev_time)  
    #print(dt)
    prev_time = current_time

    #update_starfield(dt)

    if current_state == STATE_START:
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
    elif current_state == STATE_LEVELS:
        for btn in level_selector.levels:
            btn.check_hover(mouse_pos)
        level_selector.back_button.check_hover(mouse_pos)
    elif current_state == STATE_LEVEL1:
        level1.run_button.check_hover(mouse_pos)
        level1.reset_button.check_hover(mouse_pos)

    screen.fill(BLACK)
    draw_starfield(screen)

    if current_state == STATE_START:
        update_starfield(dt)
        title_text = fonts['title_font'].render("ASTROCODE", True, CYAN)
        title_shadow = fonts['title_font'].render("ASTROCODE", True, PURPLE)
        pulse = math.sin(pygame.time.get_ticks() * 0.001) * 0.1 + 1
        scaled_title = pygame.transform.scale_by(title_text, pulse)
        scaled_shadow = pygame.transform.scale_by(title_shadow, pulse)
        scaled_rect = scaled_title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        screen.blit(scaled_shadow, (scaled_rect.x + 5, scaled_rect.y + 5))
        screen.blit(scaled_title, scaled_rect)

        subtitle_text = fonts['subtitle_font'].render("A Cosmic Coding Adventure", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 70))
        screen.blit(subtitle_text, subtitle_rect)
        start_button.draw(screen)
        quit_button.draw(screen)

        version_text = fonts['subtitle_font'].render("v1.0", True, (100, 100, 100))
        screen.blit(version_text, (WIDTH - 80, HEIGHT - 40))

    elif current_state == STATE_LEVELS:
        level_selector.draw(screen)

    elif current_state == STATE_LEVEL1:
        if level1.game_view:
            level1.draw_game(screen, mouse_pos, event)
        if level1.code_editor:
            level1.draw_code_blocks(screen)
            level1.run_button.draw(screen)
            level1.reset_button.draw(screen)
        #level1.alien.shoot_alien_bullets()
        try:
            next(level1.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level1.update(dt)

    elif current_state == STATE_LEVEL2:
        if level2.game_view:
            level2.draw_game(screen, mouse_pos, event)
        if level2.code_editor:
            level2.draw_code_blocks(screen)
            level2.run_button.draw(screen)
            level2.reset_button.draw(screen)
        #level2.alien.shoot_alien_bullets()
        try:
            next(level2.cmd_gen)
        except (StopIteration, TypeError):
            pass

        level2.update(dt)

    elif current_state == STATE_LEVEL3:
        if level3.game_view:
            level3.draw_game(screen, mouse_pos, event)
            if -20 < (level3.alien.y + level3.alien.height / 2) - (level3.player.y + level3.player.height / 2) < 20:
                level3.alien.shoot_alien_bullets()
        if level3.code_editor:
            level3.draw_code_blocks(screen)
            level3.run_button.draw(screen)
            level3.reset_button.draw(screen)
        try:
            next(level3.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level3.update(dt)

    elif current_state == STATE_LEVEL4:
        #level4.var_dict["key_press"] = None
        if level4.game_view:
            level4.draw_game(screen, mouse_pos, event)
            if -20 < (level4.alien.y + level4.alien.height / 2) - (level4.player.y + level4.player.height / 2) < 20:
                level4.alien.shoot_alien_bullets()
        if level4.code_editor:
            level4.draw_code_blocks(screen)
            level4.run_button.draw(screen)
            level4.reset_button.draw(screen)
        try:
            next(level4.cmd_gen)
        except (StopIteration, TypeError):
            pass
        level4.update(dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == STATE_START:
            if start_button.is_clicked(mouse_pos, event):
                current_state = STATE_LEVELS
            if quit_button.is_clicked(mouse_pos, event):
                running = False

        elif current_state == STATE_LEVELS:
            selected_level = level_selector.handle_click(mouse_pos, event)
            if selected_level == 1:
                current_state = STATE_LEVEL1
                level1.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
            elif selected_level == 2:
                current_state = STATE_LEVEL2
                level2.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
            elif selected_level == 3:
                current_state = STATE_LEVEL3
                level3.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])
            elif selected_level == 4:
                current_state = STATE_LEVEL4
                level4.reset_level(fonts['code_font'], fonts['title_font'], fonts['menu_font'])

        elif current_state == STATE_LEVEL1:
            if event.type == pygame.KEYDOWN:
                level1.var_dict["key_press"] = pygame.key.name(event.key)
            level1.handle_events(event, mouse_pos)
            #level1.update_bullets(dt)
            if level1.exit_to_levels:
                current_state = STATE_LEVELS
                level1.exit_to_levels = False
                #level1.success_popup = False
                #level1.success_popup1 = False

        elif current_state == STATE_LEVEL2:
            #level2.draw_all()
            level2.handle_events(event, mouse_pos)

            if level2.exit_to_levels:
                current_state = STATE_LEVELS
                level2.exit_to_levels = False

        elif current_state == STATE_LEVEL3:
            level3.handle_events(event, mouse_pos)

            if level3.exit_to_levels:
                current_state = STATE_LEVELS
                level3.exit_to_levels = False

        elif current_state == STATE_LEVEL4:
            #level4.cmd_tree = level4.traverse_cmd(level4.main_code, 1)
            if event.type == pygame.KEYDOWN:
                level4.var_dict["key_press"] = pygame.key.name(event.key)
            if event.type == pygame.KEYUP:
                level4.var_dict["key_press"] = None
            level4.handle_events(event, mouse_pos)

            if level4.exit_to_levels:
                current_state = STATE_LEVELS
                level4.exit_to_levels = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()