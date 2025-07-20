# tests/conftest.py
import pytest
from unittest.mock import Mock

# Import mocks from the new pygame_mock module
from tests.mocks.pygame_mock import MockRect, mock_constants_module  # Import sys for patching

# Ensure pygame is mocked before importing game classes
# This is crucial if game classes import pygame at the top level
# The patching is already done in pygame_mock.py, but we ensure it's loaded.

# Now import the actual game classes
from entities.player import Player
from entities.alien import Alien
from entities.bullet import Bullet
from entities.commands import Command
from levels.base_level import Level
from levels.level1 import Level1
from levels.level2 import Level2
from levels.level3 import Level3
from levels.level4 import Level4

# --- Pytest Fixtures ---
@pytest.fixture
def mock_fonts():
    """Fixture to provide mock font objects."""
    mock_code_font = Mock()
    mock_title_font = Mock()
    mock_menu_font = Mock()
    # Mock render method for fonts
    mock_code_font.render.return_value = Mock(get_width=Mock(return_value=10), get_height=Mock(return_value=10), get_rect=Mock(return_value=MockRect(0,0,10,10)))
    mock_title_font.render.return_value = Mock(get_width=Mock(return_value=20), get_height=Mock(return_value=20), get_rect=Mock(return_value=MockRect(0,0,20,20)))
    mock_menu_font.render.return_value = Mock(get_width=Mock(return_value=15), get_height=Mock(return_value=15), get_rect=Mock(return_value=MockRect(0,0,15,15)))
    return {
        'code_font': mock_code_font,
        'title_font': mock_title_font,
        'menu_font': mock_menu_font
    }

@pytest.fixture
def player_instance():
    """Fixture to provide a Player instance."""
    return Player(x=100, y=100, width=50, height=50)

@pytest.fixture
def alien_instance():
    """Fixture to provide an Alien instance."""
    return Alien(x=200, y=200, name="Alien Type A")

@pytest.fixture
def bullet_instance():
    """Fixture to provide a Bullet instance."""
    return Bullet(x=0, y=0, dx=1, dy=0, radius=mock_constants_module.BULLET_RADIUS,
                  active=True, bullet_type="circle", color=mock_constants_module.WHITE)

@pytest.fixture
def command_instance(mock_fonts):
    """Fixture to provide a Command instance."""
    mock_rect = MockRect(0, 0, 100, 30)
    return Command(cmd_type="move_up", code_font=mock_fonts['code_font'], rect=mock_rect)

@pytest.fixture
def level_instance(mock_fonts):
    """Fixture to provide a Base Level instance."""
    return Level(mock_fonts['code_font'], mock_fonts['title_font'], mock_fonts['menu_font'])

@pytest.fixture
def level1_instance(mock_fonts):
    """Fixture to provide a Level1 instance."""
    return Level1(mock_fonts['code_font'], mock_fonts['title_font'], mock_fonts['menu_font'])

@pytest.fixture
def level2_instance(mock_fonts):
    """Fixture to provide a Level2 instance."""
    return Level2(mock_fonts['code_font'], mock_fonts['title_font'], mock_fonts['menu_font'])

@pytest.fixture
def level3_instance(mock_fonts):
    """Fixture to provide a Level3 instance."""
    return Level3(mock_fonts['code_font'], mock_fonts['title_font'], mock_fonts['menu_font'])

@pytest.fixture
def level4_instance(mock_fonts):
    """Fixture to provide a Level4 instance."""
    return Level4(mock_fonts['code_font'], mock_fonts['title_font'], mock_fonts['menu_font'])