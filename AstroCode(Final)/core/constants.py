
import pygame
from pygame.examples.grid import TILE_SIZE

pygame.init()
WIDTH, HEIGHT = 1000, 800


STATE_START = 0
STATE_LEVELS = 1
STATE_LEVEL1 = 2
STATE_LEVEL2 = 3
STATE_LEVEL3 = 4
STATE_LEVEL4 = 5

ALIEN_TYPES = {
    "Alien Type A": (255, 100, 100),
    "Alien Type B": (100, 255, 100),
    "Alien Type C": (100, 100, 255)
}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
PURPLE = (150, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
FOR_LOOP_COLOR = PURPLE
DARK_OVERLAY_COLOR = (0, 0, 0, 150)

BULLET_SPEED = 180
BULLET_RADIUS = 5
TARGET_MAX_HEALTH = 200
PLAYER_MAX_HEALTH = 200
DAMAGE_PER_HIT = 25
PLAYER_AWARENESS_RANGE = 1500
COMMAND_DELAY_MS = 50
FPS = 60
ORIGINAL_CMD_WIDTH = 210
ORIGINAL_CMD_HEIGHT_LOOP = 100
TITLE_FONT_SIZE = 72
MENU_FONT_SIZE = 48
SUBTITLE_FONT_SIZE = 36
CODE_FONT_SIZE = 18

fonts = {
    'title_font': pygame.font.Font(None, TITLE_FONT_SIZE),
    'menu_font': pygame.font.Font(None, MENU_FONT_SIZE),
    'subtitle_font': pygame.font.Font(None, SUBTITLE_FONT_SIZE),
    'code_font': pygame.font.Font(None, CODE_FONT_SIZE)
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
