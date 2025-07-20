from unittest.mock import patch
import core.constants as constants
from tests.mocks.pygame_mock import MockVector2
import random
from tests.te5t_cases import player_alien_pos


def test_alien_initialization(alien_instance):
    assert alien_instance.x == 200
    assert alien_instance.y == 200
    assert alien_instance.name == "Alien Type A"
    assert alien_instance.health == constants.TARGET_MAX_HEALTH
    assert isinstance(alien_instance.pos, MockVector2)

def test_alien_take_damage(alien_instance, player_instance):
    initial_health_simulated = alien_instance.health
    with patch('orbital.core.constants.PLAYER_AWARENESS_RANGE', 200.0):
        for player_pos, alien_pos in player_alien_pos:
            alien_instance.pos = MockVector2(alien_pos[0], alien_pos[1])
            player_instance.pos = MockVector2(player_pos[0], player_pos[1])

            assert player_instance.pos.distance_to(alien_instance.pos) < constants.PLAYER_AWARENESS_RANGE

            player_instance.shoot_bullet(
                bullet_type="test",
                alien_pos=alien_instance.pos,
                color=constants.ORANGE
            )
            assert len(player_instance.bullets) == 1
            bullet = player_instance.bullets[0]
            assert bullet.active

            dt = 0.01
            while player_instance.bullet_index <= 0:
                player_instance.update_bullets(alien_instance, 0, dt)

            assert alien_instance.health < initial_health_simulated, "Alien health should have decreased after being hit by bullet."
            assert alien_instance.health == initial_health_simulated - constants.DAMAGE_PER_HIT, \
                "Alien health should have decreased by exactly one DAMAGE_PER_HIT from bullet hit."
            alien_instance.health = constants.TARGET_MAX_HEALTH
            player_instance.bullet_index = 0

def test_alien_shoot_alien_bullets(alien_instance, player_instance):
    initial_bullet_count = len(alien_instance.bullets)
    with patch('pygame.time.get_ticks', side_effect=[0, 600, 1200]):
        alien_instance.shoot_alien_bullets(player_instance, 0.1)
        assert len(alien_instance.bullets) == initial_bullet_count

        alien_instance.shoot_alien_bullets(player_instance, 0.1)
        assert len(alien_instance.bullets) == initial_bullet_count + 1
        bullet = alien_instance.bullets[0]
        assert bullet.active
        assert bullet.color == (255, 100, 255)

        alien_instance.shoot_alien_bullets(player_instance, 0.1)
        assert len(alien_instance.bullets) == initial_bullet_count + 2

        with patch('pygame.time.get_ticks', return_value=1200):
            alien_instance.shoot_alien_bullets(player_instance, 0.1)
            assert len(alien_instance.bullets) == initial_bullet_count + 2