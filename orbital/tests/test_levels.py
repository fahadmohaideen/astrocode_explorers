
import pytest
from unittest.mock import Mock, patch


from levels.base_level import Level
from levels.base_level import Player
from entities.alien import Alien
from entities.commands import Command
import core.constants as constants
from tests.mocks.pygame_mock import MockRect, MockVector2
import pygame
from orbital.tests.conftest import player_instance


def test_base_level_initialization(level_instance):
    assert level_instance.level_id == 0 
    assert isinstance(level_instance.player, Player)
    assert len(level_instance.aliens) == 0 
    assert "move_up" in level_instance.commands
    assert len(level_instance.code_blocks) > 0 

def test_level1_initialization(level1_instance):
    assert level1_instance.level_id == 1
    assert isinstance(level1_instance.target, Alien)
    assert level1_instance.target.x == 60
    assert level1_instance.target.y == 160

def test_level2_initialization(level2_instance):
    assert level2_instance.level_id == 2
    assert "if_statement" in level2_instance.commands
    assert "Alien near" in level2_instance.var_dict
    assert len(level2_instance.aliens) == 3 

def test_level3_initialization(level3_instance):
    assert level3_instance.level_id == 3
    assert "for_loop" in level3_instance.commands 
    assert "if_statement" in level3_instance.commands

def test_level4_initialization(level4_instance):
    assert level4_instance.level_id == 4
    assert "while_loop" in level4_instance.commands

def test_level_add_to_main_code(level_instance):
    initial_code_blocks = len(level_instance.main_code)
    mock_mouse_pos = (level_instance.code_area.x + 50, level_instance.code_area.y + 50)
    mock_command_type = level_instance.commands["move_up"]

    dummy_dragged_item = {
        "type": "move_up",
        "rect": MockRect(0,0,10,10),
        "cmd_type": "move_up",
        "code_font": level_instance.code_font
    }

    level_instance.add_to_main_code(level_instance.main_code, level_instance.code_area, dummy_dragged_item, mock_mouse_pos, 0, None)
    assert len(level_instance.main_code) == initial_code_blocks + 1
    assert level_instance.main_code[0].cmd_type == "move_up"

def test_level_execute_commands_move_up(level_instance):
    initial_player_pos_y = level_instance.player.pos.y
    move_up_cmd = Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    level_instance.main_code = [move_up_cmd]

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen)
    except StopIteration:
        pass

    assert level_instance.player.pos.y < initial_player_pos_y
    expected_change_y = level_instance.player.speed * (constants.COMMAND_DELAY_MS / 1000.0) * 10
    assert level_instance.player.pos.y == initial_player_pos_y - 50


def test_level_execute_commands_for_loop(level_instance):
    initial_player_pos_y = level_instance.player.pos.y
    for_loop_cmd = Command(cmd_type="for_loop", iterations=3, code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    move_up_cmd = Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    for_loop_cmd.nested_commands.append(move_up_cmd)
    level_instance.main_code = [for_loop_cmd]

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen)
        next(cmd_gen)
        next(cmd_gen)
    except StopIteration:
        pass

    assert level_instance.player.pos.y == initial_player_pos_y - 3*50

def test_level_execute_commands_if_statement(level_instance):
    initial_player_pos_y = level_instance.player.pos.y
    if_cmd = Command(cmd_type="if_statement", conditions={"var": "Alien near", "op": "==", "val": True},
                     condition_var="Alien near", condition_op="==", condition_val=True,
                     code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    move_up_cmd = Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    if_cmd.nested_commands.append(move_up_cmd)
    level_instance.main_code = [if_cmd]

    level_instance.var_dict["Alien near"] = [True, None, None] 

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen) 
    except StopIteration:
        pass

    assert level_instance.player.pos.y == initial_player_pos_y - 50

    level_instance.player.pos.y = initial_player_pos_y 
    level_instance.var_dict["Alien near"] = [False, None, None] 

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen)
    except StopIteration:
        pass

    assert level_instance.player.pos.y == initial_player_pos_y

def test_level_execute_commands_shoot(level_instance, alien_instance):
    level_instance.curr_nearest_alien = alien_instance
    shoot_cmd = Command(cmd_type="shoot", shoot_bullet_type="Type A",
                        code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    level_instance.main_code = [shoot_cmd]

    initial_bullets = len(level_instance.player.bullets)

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen) 
    except StopIteration:
        pass

    assert len(level_instance.player.bullets) == initial_bullets + 1
    assert level_instance.player.bullets[-1].bullet_type == "Type A"

def test_level_handle_events_drag_and_drop(level_instance):
    level_instance.code_blocks = [Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))]
    mock_mouse_pos_palette = (level_instance.code_blocks[0].rect.x + 5, level_instance.code_blocks[0].rect.y + 5)
    mock_event_mouse_down = Mock(type=pygame.MOUSEBUTTONDOWN, button=2, pos=mock_mouse_pos_palette)
    level_instance.handle_events(mock_event_mouse_down, mock_mouse_pos_palette)
    assert level_instance.dragging is not None
    assert level_instance.dragging["type"] == level_instance.code_blocks[0].cmd_type

    mock_mouse_pos_code_area = (level_instance.code_area.x + 50, level_instance.code_area.y + 50)
    mock_event_mouse_up = Mock(type=pygame.MOUSEBUTTONUP, button=2, pos=mock_mouse_pos_code_area)
    initial_main_code_len = len(level_instance.main_code)
    level_instance.handle_events(mock_event_mouse_up, mock_mouse_pos_code_area)
    assert level_instance.dragging is None
    assert len(level_instance.main_code) == initial_main_code_len + 1
    assert level_instance.main_code[0].cmd_type == "move_up"

def test_level_handle_events_run_button(level_instance):
    level_instance.main_code = [Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10)), Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))]
    level_instance.run_button.rect.x = 625  
    level_instance.run_button.rect.y = 725 

    mock_mouse_pos = (level_instance.run_button.rect.x + 5, level_instance.run_button.rect.y + 5)
    mock_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=mock_mouse_pos)

    level_instance.handle_events(mock_event, mock_mouse_pos)
    assert not level_instance.code_editor
    assert level_instance.game_view
    assert level_instance.cmd_gen is not None 

def test_level_handle_events_reset_button(level_instance):
    level_instance.main_code.append(Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10)))
    assert len(level_instance.main_code) > 0

    level_instance.run_button.rect.x = 375  
    level_instance.run_button.rect.y = 725 
    mock_mouse_pos = (level_instance.reset_button.rect.x + 5, level_instance.reset_button.rect.y + 5)
    mock_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=mock_mouse_pos)

    level_instance.handle_events(mock_event, mock_mouse_pos)
    assert len(level_instance.main_code) == 0 

def test_level2_update_player_movement(level2_instance):
    initial_player_pos = MockVector2(level2_instance.player.pos.x, level2_instance.player.pos.y)
    dt = 0.1
    keys_pressed = {pygame.K_w: True, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: True, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False}
    level2_instance.update(dt, keys_pressed)
    assert level2_instance.player.pos.y == initial_player_pos.y - level2_instance.player.speed * dt
    assert level2_instance.moving

    level2_instance.player.pos = MockVector2(initial_player_pos.x, initial_player_pos.y) 
    keys_pressed = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False}
    level2_instance.update(dt, keys_pressed)
    assert level2_instance.player.pos.y == initial_player_pos.y
    assert not level2_instance.moving

def test_level2_update_alien_near_detection(level2_instance, alien_instance):
    alien_instance.pos = MockVector2(level2_instance.player.pos.x + 500, level2_instance.player.pos.y + 500)
    level2_instance.aliens = [alien_instance]
    level2_instance.update(0.1, {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False})
    assert not level2_instance.var_dict["Alien near"][0]
    assert not level2_instance.var_dict[alien_instance.name][0]
    assert level2_instance.var_dict[alien_instance.name][1] is None
    assert level2_instance.curr_nearest_alien is None

    alien_instance.pos = MockVector2(level2_instance.player.pos.x + 50, level2_instance.player.pos.y + 50)
    level2_instance.aliens = [alien_instance] 
    level2_instance.update(0.1, {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False})
    assert level2_instance.var_dict["Alien near"][0]
    assert level2_instance.var_dict[alien_instance.name][0]
    assert level2_instance.var_dict[alien_instance.name][1] == alien_instance
    assert level2_instance.curr_nearest_alien == alien_instance

"""def test_level3_update_alien_shooting(level3_instance, player_instance, alien_instance):
    alien_instance.pos = MockVector2(player_instance.pos.x + 50, player_instance.pos.y + 50)
    level3_instance.aliens = [alien_instance]
    level3_instance.player = player_instance

    initial_alien_bullets = len(alien_instance.bullets)
    with patch('pygame.time.get_ticks', side_effect=[0, 600, 1200]): 
        level3_instance.update(0.1, {})
        assert len(alien_instance.bullets) == initial_alien_bullets

        level3_instance.update(0.1, {})
        assert len(alien_instance.bullets) == initial_alien_bullets + 1
        assert alien_instance.bullets[-1].active # Check if the bullet is active
        assert alien_instance.bullets[-1].color == (255, 100, 255) 

        level3_instance.update(0.1, {})
        assert len(alien_instance.bullets) == initial_alien_bullets + 1

        with patch('pygame.time.get_ticks', return_value=1200):
            level3_instance.update(0.1, {})
            assert len(alien_instance.bullets) == initial_alien_bullets + 2"""