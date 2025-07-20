# tests/test_player.py
import pytest
from unittest.mock import patch
# Import player and constants from the main game code
# Import mock constants from your test mocks (they are sys.modules patched)
import core.constants as constants
# Import MockVector2 from your test mocks if needed for direct instantiation in tests
from tests.mocks.pygame_mock import MockVector2
from tests.te5t_cases import player_alien_pos
from orbital.tests.conftest import alien_instance


def test_player_initialization(player_instance):
    assert player_instance.x == 100
    assert player_instance.y == 100
    assert player_instance.width == 50
    assert player_instance.height == 50
    assert player_instance.health == constants.PLAYER_MAX_HEALTH
    assert isinstance(player_instance.pos, MockVector2)
    assert player_instance.pos.x == 125 # Center of player
    assert player_instance.pos.y == 125 # Center of player
    assert len(player_instance.bullets) == 0
    assert len(player_instance.bullet_pool) == 0

def test_player_take_damage(player_instance, alien_instance):
    initial_health_simulated = player_instance.health
    with patch('orbital.core.constants.PLAYER_AWARENESS_RANGE', 200.0):
        for player_pos, alien_pos in player_alien_pos:
            alien_instance.pos = MockVector2(alien_pos[0], alien_pos[1])
            player_instance.pos = MockVector2(player_pos[0], player_pos[1])

            # Verify player is now in range (pre-condition for shooting)
            assert player_instance.pos.distance_to(alien_instance.pos) < constants.PLAYER_AWARENESS_RANGE

            # 2.2 Player shoots at the alien
            # player_instance.damage_dealt = False  # Reset this flag for the test
            alien_instance.shoot_bullet(
                bullet_type="test",
                alien_pos=player_instance.pos,
                color=constants.ORANGE
            )
            assert len(alien_instance.bullets) == 1
            bullet = alien_instance.bullets[0]
            assert bullet.active

            # 2.3 Simulate bullet travel and collision using player.update_bullets
            dt = 0.01  # Small-time step for bullet updates
            while alien_instance.bullet_index <= 0:
                alien_instance.update_bullets(player_instance, 0, dt)  # level_id is not relevant for this core mechanic

            assert player_instance.health < initial_health_simulated, "Alien health should have decreased after being hit by bullet."
            assert player_instance.health == initial_health_simulated - constants.DAMAGE_PER_HIT, \
                "Alien health should have decreased by exactly one DAMAGE_PER_HIT from bullet hit."
            player_instance.health = constants.TARGET_MAX_HEALTH
            alien_instance.bullet_index = 0

def test_player_shoot_bullet(player_instance):
    target_pos = MockVector2(200, 100)
    player_instance.shoot_bullet(bullet_type="circle", alien_pos=target_pos, color=constants.ORANGE)
    assert len(player_instance.bullets) == 1
    bullet = player_instance.bullets[0]
    assert bullet.active
    assert bullet.bullet_type == "circle"
    assert bullet.color == constants.ORANGE
    # Check if bullet direction is generally correct (towards target)
    assert pytest.approx(bullet.dx * bullet.dx + bullet.dy * bullet.dy, rel=1e-5) == 1.0

"""def test_player_update_bullets_collision(player_instance, alien_instance):
    # Position alien to be hit by a bullet fired from player
    alien_instance.pos = MockVector2(player_instance.pos.x + 50, player_instance.pos.y)
    initial_alien_health = alien_instance.health

    player_instance.shoot_bullet(bullet_type="circle", alien_pos=alien_instance.pos, color=constants.ORANGE)
    bullet = player_instance.bullets[0]

    dt = 0.1 # Small time step
    # Simulate a few updates for the bullet to move and potentially hit
    # The number of iterations might need adjustment based on BULLET_SPEED and distance
    for _ in range(10):
        player_instance.update_bullets(alien_instance, 0, dt) # level_id doesn't matter for this test
        if not bullet.active:
            break

    assert not bullet.active # Bullet should become inactive after hitting
    assert player_instance.damage_dealt
    assert alien_instance.health < initial_alien_health # Alien should have taken damage"""