
import pytest
from unittest.mock import patch
import core.constants as constants
from core.constants import BULLET_SPEED
from tests.mocks.pygame_mock import MockVector2
from tests.te5t_cases import player_alien_pos
from tests.conftest import alien_instance


def test_player_initialization(player_instance):
    assert player_instance.x == 100
    assert player_instance.y == 100
    assert player_instance.width == 50
    assert player_instance.height == 50
    assert player_instance.health == constants.PLAYER_MAX_HEALTH
    assert isinstance(player_instance.pos, MockVector2)
    assert player_instance.pos.x == 125
    assert player_instance.pos.y == 125
    assert len(player_instance.bullets) == 0
    assert len(player_instance.bullet_pool) == 0

def test_player_take_damage(player_instance, alien_instance):
    initial_health_simulated = player_instance.health
    with patch('core.constants.PLAYER_AWARENESS_RANGE', 200.0):
        for player_pos, alien_pos in player_alien_pos:
            alien_instance.pos = MockVector2(alien_pos[0], alien_pos[1])
            player_instance.pos = MockVector2(player_pos[0], player_pos[1])

            assert player_instance.pos.distance_to(alien_instance.pos) < constants.PLAYER_AWARENESS_RANGE

            alien_instance.shoot_bullet(
                target_pos=player_instance.pos,
                color=None
            )
            assert len(alien_instance.bullets) == 1
            bullet = alien_instance.bullets[0]
            assert bullet.active

            dt = 0.01
            while alien_instance.bullet_index <= 0:
                alien_instance.update_bullets(player_instance, 0, dt)

            assert player_instance.health < initial_health_simulated
            assert player_instance.health == initial_health_simulated - constants.DAMAGE_PER_HIT, \
                "Alien health should have decreased by exactly one DAMAGE_PER_HIT from bullet hit."
            player_instance.health = constants.TARGET_MAX_HEALTH
            alien_instance.bullet_index = 0

def test_player_shoot_bullet(player_instance):
    target_pos = MockVector2(200, 100)
    player_instance.shoot_bullet(bullet_type="circle", direction=(target_pos - player_instance.pos), color=constants.ORANGE)
    assert len(player_instance.bullets) == 1
    bullet = player_instance.bullets[0]
    assert bullet.active
    assert bullet.bullet_type == "circle"
    assert bullet.color == constants.ORANGE
    assert pytest.approx((bullet.dx/BULLET_SPEED)**2 + (bullet.dy/BULLET_SPEED)**2, rel=1e-5) == (player_instance.pos.distance_to(target_pos))**2

"""def test_player_update_bullets_collision(player_instance, alien_instance):
    alien_instance.pos = MockVector2(player_instance.pos.x + 50, player_instance.pos.y)
    initial_alien_health = alien_instance.health

    player_instance.shoot_bullet(bullet_type="circle", alien_pos=alien_instance.pos, color=constants.ORANGE)
    bullet = player_instance.bullets[0]

    dt = 0.1
    for _ in range(10):
        player_instance.update_bullets(alien_instance, 0, dt)
        if not bullet.active:
            break

    assert not bullet.active
    assert player_instance.damage_dealt
    assert alien_instance.health < initial_alien_health"""