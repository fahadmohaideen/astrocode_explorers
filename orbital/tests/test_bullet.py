
import core.constants as constants
from tests.mocks.pygame_mock import MockVector2

def test_bullet_initialization(bullet_instance):
    assert bullet_instance.x == 0
    assert bullet_instance.y == 0
    assert bullet_instance.dx == 1
    assert bullet_instance.dy == 0
    assert bullet_instance.radius == constants.BULLET_RADIUS
    assert bullet_instance.active
    assert bullet_instance.bullet_type == "circle"
    assert bullet_instance.color == constants.WHITE
    assert isinstance(bullet_instance.pos, MockVector2)

def test_bullet_movement(bullet_instance):
    initial_pos = MockVector2(bullet_instance.pos.x, bullet_instance.pos.y)
    dt = 0.1
    bullet_instance.pos.x += bullet_instance.dx * dt * constants.BULLET_SPEED
    bullet_instance.pos.y += bullet_instance.dy * dt * constants.BULLET_SPEED
    assert bullet_instance.pos.x == initial_pos.x + 1 * 0.1 * 180
    assert bullet_instance.pos.y == initial_pos.y + 0 * 0.1 * 180