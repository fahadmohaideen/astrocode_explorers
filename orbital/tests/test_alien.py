# tests/test_alien.py
from unittest.mock import patch

# Import Alien and constants from the main game code
import core.constants as constants # Import mock constants
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

            # Verify player is now in range (pre-condition for shooting)
            assert player_instance.pos.distance_to(alien_instance.pos) < constants.PLAYER_AWARENESS_RANGE

            # 2.2 Player shoots at the alien
            # player_instance.damage_dealt = False  # Reset this flag for the test
            player_instance.shoot_bullet(
                bullet_type="test",
                alien_pos=alien_instance.pos,
                color=constants.ORANGE
            )
            assert len(player_instance.bullets) == 1
            bullet = player_instance.bullets[0]
            assert bullet.active

            # 2.3 Simulate bullet travel and collision using player.update_bullets
            dt = 0.01  # Small-time step for bullet updates
            while player_instance.bullet_index <= 0:
                player_instance.update_bullets(alien_instance, 0, dt)  # level_id is not relevant for this core mechanic

            #assert bullet.pos == player_instance.pos
            assert alien_instance.health < initial_health_simulated, "Alien health should have decreased after being hit by bullet."
            assert alien_instance.health == initial_health_simulated - constants.DAMAGE_PER_HIT, \
                "Alien health should have decreased by exactly one DAMAGE_PER_HIT from bullet hit."
            alien_instance.health = constants.TARGET_MAX_HEALTH
            player_instance.bullet_index = 0

def test_alien_shoot_alien_bullets(alien_instance, player_instance):
    initial_bullet_count = len(alien_instance.bullets)
    # Mock get_ticks to simulate time passing
    with patch('pygame.time.get_ticks', side_effect=[0, 600, 1200]): # Simulate 600ms then another 600ms
        alien_instance.shoot_alien_bullets(player_instance, 0.1) # First call, no shot (prev_time is 0)
        assert len(alien_instance.bullets) == initial_bullet_count

        alien_instance.shoot_alien_bullets(player_instance, 0.1) # Second call, should shoot
        assert len(alien_instance.bullets) == initial_bullet_count + 1
        bullet = alien_instance.bullets[0]
        assert bullet.active
        assert bullet.color == (255, 100, 255) # Hardcoded color in alien.py

        alien_instance.shoot_alien_bullets(player_instance, 0.1) # Third call, no shot yet
        assert len(alien_instance.bullets) == initial_bullet_count + 2

        # Simulate more time for another shot
        with patch('pygame.time.get_ticks', return_value=1200): # Force time ahead for next shot
            alien_instance.shoot_alien_bullets(player_instance, 0.1)
            assert len(alien_instance.bullets) == initial_bullet_count + 2