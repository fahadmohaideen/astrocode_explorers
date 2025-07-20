# tests/test_commands.py

# Import Command from the main game code
from entities.commands import Command
from tests.mocks.pygame_mock import MockRect # Import MockRect for direct instantiation if needed

def test_command_basic_initialization(command_instance):
    assert command_instance.cmd_type == "move_up"
    assert command_instance.text == "Move Up"
    assert not command_instance.is_loop()
    assert not command_instance.is_conditional()

def test_command_for_loop_initialization(mock_fonts):
    mock_rect = MockRect(0, 0, 100, 30)
    cmd = Command(cmd_type="for_loop", iterations=5, code_font=mock_fonts['code_font'], rect=mock_rect)
    assert cmd.cmd_type == "for_loop"
    assert cmd.iterations == 5
    assert cmd.is_loop()
    assert not cmd.is_conditional()
    assert len(cmd.nested_commands) == 0 # Should be empty by default

def test_command_if_statement_initialization(mock_fonts):
    mock_rect = MockRect(0, 0, 100, 30)
    cmd = Command(cmd_type="if_statement", conditions={"var": "health", "op": ">", "val": "50"},
                  code_font=mock_fonts['code_font'], rect=mock_rect)
    assert cmd.cmd_type == "if_statement"
    assert cmd.is_conditional()
    assert not cmd.is_loop()
    assert cmd.conditions["var"] == "health"
    assert len(cmd.nested_commands) == 0 # Should be empty by default