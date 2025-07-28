
import sys
from unittest.mock import Mock, patch
import math
import random

sys.modules['pygame'] = Mock()
sys.modules['pygame.locals'] = Mock()
sys.modules['pygame.font'] = Mock()
sys.modules['pygame.display'] = Mock()
sys.modules['pygame.image'] = Mock()
sys.modules['pygame.transform'] = Mock()
sys.modules['pygame.time'] = Mock()
sys.modules['pygame.math'] = Mock()

class MockVector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return MockVector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return MockVector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return MockVector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return MockVector2(self.x / scalar, self.y / scalar)

    def distance_to(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

    def normalize(self):
        mag = self.length()
        if mag == 0:
            return MockVector2(0, 0)
        return MockVector2(self.x / mag, self.y / mag)

    def length(self):
        return (self.x**2 + self.y**2)**0.5

    def angle_to(self, other):
        dot_product = self.x * other.x + self.y * other.y
        magnitude_product = self.length() * other.length()
        if magnitude_product == 0:
            return 0
        angle_rad = math.acos(max(-1, min(1, dot_product / magnitude_product)))
        return math.degrees(angle_rad)

    def __repr__(self):
        return f"MockVector2({self.x}, {self.y})"

original_vector2 = None
if hasattr(sys.modules['pygame'], 'math') and hasattr(sys.modules['pygame'].math, 'Vector2'):
    original_vector2 = sys.modules['pygame'].math.Vector2
sys.modules['pygame'].Vector2 = MockVector2
sys.modules['pygame.math'].Vector2 = MockVector2


class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.top = y
        self.left = x
        self.bottom = y + height
        self.right = x + width
        self.centerx = x + width / 2
        self.centery = y + height / 2

    def collidepoint(self, pos):
        return self.x <= pos[0] <= self.x + self.width and \
               self.y <= pos[1] <= self.y + self.height

    def colliderect(self, other):
        return not (self.right < other.left or self.left > other.right or
                    self.bottom < other.top or self.top > other.bottom)

    def __repr__(self):
        return f"MockRect({self.x}, {self.y}, {self.width}, {self.height})"

sys.modules['pygame'].Rect = MockRect
sys.modules['pygame'].Surface = Mock
sys.modules['pygame'].time.get_ticks = Mock(return_value=0)

mock_constants_module = Mock()
mock_constants_module.WIDTH = 800
mock_constants_module.HEIGHT = 600
mock_constants_module.PLAYER_MAX_HEALTH = 100
mock_constants_module.TARGET_MAX_HEALTH = 100
mock_constants_module.BULLET_RADIUS = 5
mock_constants_module.BULLET_SPEED = 180
mock_constants_module.DAMAGE_PER_HIT = 10
mock_constants_module.FOR_LOOP_COLOR = (100, 100, 100)
mock_constants_module.WHITE = (255, 255, 255)
mock_constants_module.BLACK = (0, 0, 0)
mock_constants_module.CYAN = (0, 255, 255)
mock_constants_module.ORANGE = (255, 165, 0)
mock_constants_module.BLUE = (0, 0, 255)
mock_constants_module.GREEN = (0, 255, 0)
mock_constants_module.RED = (255, 0, 0)
mock_constants_module.DARK_GRAY = (50, 50, 50)
mock_constants_module.DARK_OVERLAY_COLOR = (0, 0, 0, 150)
mock_constants_module.ORIGINAL_CMD_WIDTH = 200
mock_constants_module.ORIGINAL_CMD_HEIGHT_LOOP = 50
mock_constants_module.CODE_FONT_SIZE = 20
mock_constants_module.ALIEN_TYPES = {"Alien Type A": (10,10,10), "Alien Type B": (20,20,20), "Alien Type C": (30,30,30), "Alien Type A": (255, 0, 0), "Alien Type B": (0, 255, 0), "Alien Type C": (0, 0, 255)}
mock_constants_module.screen = Mock()
#sys.modules['core.constants'] = mock_constants_module


mock_bullet_shapes_module = Mock()
mock_bullet_shapes_module.Circle = Mock()
mock_bullet_shapes_module.Square = Mock()
mock_bullet_shapes_module.Triangle = Mock()
sys.modules['entities.bullet_shapes'] = mock_bullet_shapes_module

mock_button_module = Mock()
mock_button_module.Button = Mock()
sys.modules['ui.button'] = mock_button_module
mock_level_selector_module = Mock()
mock_level_selector_module.LevelSelector = Mock()
sys.modules['ui.level_selector'] = mock_level_selector_module

mock_utils_module = Mock()
mock_utils_module.draw_starfield = Mock()
mock_utils_module.update_starfield = Mock()
sys.modules['core.utils'] = mock_utils_module


