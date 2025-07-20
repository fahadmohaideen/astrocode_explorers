# tests/test_levels.py
import pytest
from unittest.mock import Mock, patch

# Import game classes and constants
from levels.base_level import Level
from levels.base_level import Player
from entities.alien import Alien
from entities.commands import Command # Needed for creating Command objects in tests
import core.constants as constants # Import mock constants
from tests.mocks.pygame_mock import MockRect, MockVector2 # Import mocks for direct instantiation
import pygame
from orbital.tests.conftest import player_instance


#from orbital.entities.player import Player


def test_base_level_initialization(level_instance):
    assert level_instance.level_id == 0 # Base level id
    #assert isinstance(level_instance.player, Player) # Check if it's an instance of the Player class
    assert isinstance(level_instance.player, Player)
    assert len(level_instance.aliens) == 0 # No aliens spawned by default in base level init
    assert "move_up" in level_instance.commands
    assert len(level_instance.code_blocks) > 0 # Should have initial commands

def test_level1_initialization(level1_instance):
    assert level1_instance.level_id == 1
    assert isinstance(level1_instance.target, Alien)
    assert level1_instance.target.x == 60
    assert level1_instance.target.y == 160

def test_level2_initialization(level2_instance):
    assert level2_instance.level_id == 2
    assert "if_statement" in level2_instance.commands
    assert "Alien near" in level2_instance.var_dict
    assert len(level2_instance.aliens) == 3 # Should spawn 3 aliens

def test_level3_initialization(level3_instance):
    assert level3_instance.level_id == 3
    # Level3 inherits from Level2, so it should have similar initializations
    assert "for_loop" in level3_instance.commands # Added in Level3 init
    assert "if_statement" in level3_instance.commands

def test_level4_initialization(level4_instance):
    assert level4_instance.level_id == 4
    assert "while_loop" in level4_instance.commands

def test_level_add_to_main_code(level_instance):
    initial_code_blocks = len(level_instance.main_code)
    # Mock mouse position within the code area
    mock_mouse_pos = (level_instance.code_area.x + 50, level_instance.code_area.y + 50)
    # Assuming "move_up" is the first command in level_instance.code_blocks (from base_level init)
    mock_command_type = level_instance.commands["move_up"] # Use the actual command dictionary entry

    # Create a dummy dragged item to simulate the drag-and-drop mechanism
    dummy_dragged_item = {
        "type": "move_up",
        "rect": MockRect(0,0,10,10), # Dummy rect, position doesn't matter for `add_to_main_code`
        "cmd_type": "move_up",
        "code_font": level_instance.code_font
    }

    # Simulate add_to_main_code's internal call with the dragged item
    # This test directly calls the method that `handle_events` would eventually call
    level_instance.add_to_main_code(level_instance.main_code, level_instance.code_area, dummy_dragged_item, mock_mouse_pos, 0, None)
    assert len(level_instance.main_code) == initial_code_blocks + 1
    assert level_instance.main_code[0].cmd_type == "move_up"

def test_level_execute_commands_move_up(level_instance):
    initial_player_pos_y = level_instance.player.pos.y
    # Create a simple "move_up" command
    move_up_cmd = Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    level_instance.main_code = [move_up_cmd]

    # Execute the command using the generator
    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen) # Execute the move_up command
    except StopIteration:
        pass

    # Player's y position should decrease (move up)
    # Player's speed is 300, dt in Level.update is 0.1, so it should move by 30
    assert level_instance.player.pos.y < initial_player_pos_y
    # This might be tricky with camera_offset, so let's assert based on direct change if possible.
    # From player.py, movement is self.pos.y -= dt * self.speed * 10 if cmd_type == "move_up" else -1
    # Assuming player speed is default (300 from Player.__init__ if not set), and move amount is constants.PLAYER_MOVE_AMOUNT (not explicitly mocked, so it uses 10 here)
    # Let's verify the change relative to current player speed
    expected_change_y = level_instance.player.speed * (constants.COMMAND_DELAY_MS / 1000.0) * 10
    # The actual movement in Player.py for "move_up" looks like `self.pos.y -= dt * self.speed * 10`
    # Given that `dt` is handled within the generator (it doesn't directly consume the `dt` passed to `level.update`),
    # we need to consider the discrete step of the command execution.
    # The `move_up` command's effect on player.pos is: player.pos.y -= self.player.speed * (COMMAND_DELAY_MS / 1000.0)
    # (Based on level.py: self.player.pos.y -= self.player.speed * (COMMAND_DELAY_MS / 1000.0) # Move up)
    # So, the actual move amount should be self.player.speed * (COMMAND_DELAY_MS / 1000.0)
    # COMMAND_DELAY_MS is 500, so 0.5. Player speed is 300. So 300 * 0.5 = 150.
    # The initial player position in base_level is (250, 300) so center (275, 325)
    # initial_player_pos_y is 325. Expected new_pos_y = 325 - 150 = 175
    assert level_instance.player.pos.y == initial_player_pos_y - 50


def test_level_execute_commands_for_loop(level_instance):
    initial_player_pos_y = level_instance.player.pos.y
    # Create a for loop with a nested "move_up" command
    for_loop_cmd = Command(cmd_type="for_loop", iterations=3, code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    move_up_cmd = Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    for_loop_cmd.nested_commands.append(move_up_cmd)
    level_instance.main_code = [for_loop_cmd]

    # Execute the commands using the generator
    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen)
        next(cmd_gen)
        next(cmd_gen)
    except StopIteration:
        pass

    # Player's y position should decrease twice
    # Each move_up moves by 150 (from previous test)
    assert level_instance.player.pos.y == initial_player_pos_y - 3*50

def test_level_execute_commands_if_statement(level_instance):
    initial_player_pos_y = level_instance.player.pos.y
    # Create an if statement that evaluates to True, with a nested "move_up"
    if_cmd = Command(cmd_type="if_statement", conditions={"var": "Alien near", "op": "==", "val": True},
                     condition_var="Alien near", condition_op="==", condition_val=True,
                     code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    move_up_cmd = Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    if_cmd.nested_commands.append(move_up_cmd)
    level_instance.main_code = [if_cmd]

    # Set the condition to True in var_dict
    level_instance.var_dict["Alien near"] = [True, None, None] # Set alien near to True

    # Execute the commands
    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen) # Should execute the nested move_up
    except StopIteration:
        pass

    assert level_instance.player.pos.y == initial_player_pos_y - 50

    # Test when condition is False
    level_instance.player.pos.y = initial_player_pos_y # Reset player position
    level_instance.var_dict["Alien near"] = [False, None, None] # Set condition to False

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        # We expect the generator to yield once for the if statement itself
        # but not for its nested commands if the condition is false.
        next(cmd_gen)
    except StopIteration:
        pass

    assert level_instance.player.pos.y == initial_player_pos_y # Should not have moved

def test_level_execute_commands_shoot(level_instance, alien_instance):
    # Setup for shoot command
    level_instance.curr_nearest_alien = alien_instance
    shoot_cmd = Command(cmd_type="shoot", shoot_bullet_type="Type A",
                        code_font=level_instance.code_font, rect=MockRect(0,0,10,10))
    level_instance.main_code = [shoot_cmd]

    initial_bullets = len(level_instance.player.bullets)

    cmd_gen = level_instance.execute_commands(level_instance.main_code, None)
    try:
        next(cmd_gen) # Execute the shoot command
    except StopIteration:
        pass

    assert len(level_instance.player.bullets) == initial_bullets + 1
    assert level_instance.player.bullets[-1].bullet_type == "Type A"

def test_level_handle_events_drag_and_drop(level_instance):
    #level_instance.main_code = []
    level_instance.code_blocks = [Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))]
    # Simulate dragging a command from the palette
    mock_mouse_pos_palette = (level_instance.code_blocks[0].rect.x + 5, level_instance.code_blocks[0].rect.y + 5)
    mock_event_mouse_down = Mock(type=pygame.MOUSEBUTTONDOWN, button=2, pos=mock_mouse_pos_palette)
    level_instance.handle_events(mock_event_mouse_down, mock_mouse_pos_palette)
    assert level_instance.dragging is not None
    # Assuming "move_up" is the first command in the palette
    assert level_instance.dragging["type"] == level_instance.code_blocks[0].cmd_type

    # Simulate dropping the command into the code area
    mock_mouse_pos_code_area = (level_instance.code_area.x + 50, level_instance.code_area.y + 50)
    mock_event_mouse_up = Mock(type=pygame.MOUSEBUTTONUP, button=2, pos=mock_mouse_pos_code_area)
    initial_main_code_len = len(level_instance.main_code)
    level_instance.handle_events(mock_event_mouse_up, mock_mouse_pos_code_area)
    assert level_instance.dragging is None
    assert len(level_instance.main_code) == initial_main_code_len + 1
    assert level_instance.main_code[0].cmd_type == "move_up"

def test_level_handle_events_run_button(level_instance):
    # Mock the run button to be clicked (its is_clicked method will be used)
    # The Button mock from conftest.py already has is_clicked.
    #level_instance.run_button.is_clicked.return_value = True
    level_instance.main_code = [Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10)), Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10))]
    level_instance.run_button.rect.x = 625  # Set a mock integer value for x
    level_instance.run_button.rect.y = 725  # Set a mock integer value for y

    mock_mouse_pos = (level_instance.run_button.rect.x + 5, level_instance.run_button.rect.y + 5)
    mock_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=mock_mouse_pos)

    level_instance.handle_events(mock_event, mock_mouse_pos)
    assert not level_instance.code_editor
    assert level_instance.game_view
    assert level_instance.cmd_gen is not None # Generator should be initialized

def test_level_handle_events_reset_button(level_instance):
    level_instance.main_code.append(Command(cmd_type="move_up", code_font=level_instance.code_font, rect=MockRect(0,0,10,10)))
    assert len(level_instance.main_code) > 0

    # Mock the reset button to be clicked
    #level_instance.reset_button.is_clicked.return_value = True
    level_instance.run_button.rect.x = 375  # Set a mock integer value for x
    level_instance.run_button.rect.y = 725  # Set a mock integer value for y
    mock_mouse_pos = (level_instance.reset_button.rect.x + 5, level_instance.reset_button.rect.y + 5)
    mock_event = Mock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=mock_mouse_pos)

    level_instance.handle_events(mock_event, mock_mouse_pos)
    assert len(level_instance.main_code) == 0 # Main code should be cleared

def test_level2_update_player_movement(level2_instance):
    initial_player_pos = MockVector2(level2_instance.player.pos.x, level2_instance.player.pos.y)
    dt = 0.1
    # Simulate 'W' key press
    keys_pressed = {pygame.K_w: True, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: True, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False}
    level2_instance.update(dt, keys_pressed)
    # Player's speed is 300, dt is 0.1, so it should move by 300 * 0.1 = 30
    assert level2_instance.player.pos.y == initial_player_pos.y - level2_instance.player.speed * dt
    assert level2_instance.moving

    # Simulate no key press
    level2_instance.player.pos = MockVector2(initial_player_pos.x, initial_player_pos.y) # Reset position
    keys_pressed = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False}
    level2_instance.update(dt, keys_pressed)
    assert level2_instance.player.pos.y == initial_player_pos.y # Should not move
    assert not level2_instance.moving

def test_level2_update_alien_near_detection(level2_instance, alien_instance):
    # Position alien far away
    alien_instance.pos = MockVector2(level2_instance.player.pos.x + 500, level2_instance.player.pos.y + 500)
    level2_instance.aliens = [alien_instance]
    level2_instance.update(0.1, {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False})
    assert not level2_instance.var_dict["Alien near"][0]
    assert not level2_instance.var_dict[alien_instance.name][0]
    assert level2_instance.var_dict[alien_instance.name][1] is None
    assert level2_instance.curr_nearest_alien is None

    # Position alien near (within PLAYER_AWARENESS_RANGE which is 200)
    alien_instance.pos = MockVector2(level2_instance.player.pos.x + 50, level2_instance.player.pos.y + 50)
    level2_instance.aliens = [alien_instance] # Ensure the alien list is updated
    level2_instance.update(0.1, {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False})
    assert level2_instance.var_dict["Alien near"][0]
    assert level2_instance.var_dict[alien_instance.name][0]
    assert level2_instance.var_dict[alien_instance.name][1] == alien_instance
    assert level2_instance.curr_nearest_alien == alien_instance

"""def test_level3_update_alien_shooting(level3_instance, player_instance, alien_instance):
    # Ensure alien shoots when player is near
    alien_instance.pos = MockVector2(player_instance.pos.x + 50, player_instance.pos.y + 50)
    level3_instance.aliens = [alien_instance]
    level3_instance.player = player_instance

    initial_alien_bullets = len(alien_instance.bullets)
    # Patch pygame.time.get_ticks for a more robust test
    with patch('pygame.time.get_ticks', side_effect=[0, 600, 1200]): # Simulate time for alien to shoot
        level3_instance.update(0.1, {}) # First update, no shot (prev_time is 0)
        assert len(alien_instance.bullets) == initial_alien_bullets

        level3_instance.update(0.1, {}) # Second update, should shoot after 600ms
        assert len(alien_instance.bullets) == initial_alien_bullets + 1
        assert alien_instance.bullets[-1].active # Check if the bullet is active
        assert alien_instance.bullets[-1].color == (255, 100, 255) # Hardcoded color in alien.py

        level3_instance.update(0.1, {}) # Third update, no shot yet (not enough time passed since last shot)
        assert len(alien_instance.bullets) == initial_alien_bullets + 1

        # Simulate more time for another shot
        with patch('pygame.time.get_ticks', return_value=1200):
            level3_instance.update(0.1, {}) # Should shoot again
            assert len(alien_instance.bullets) == initial_alien_bullets + 2"""