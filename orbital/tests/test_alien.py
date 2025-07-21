# tests/test_alien.py
from unittest.mock import patch, Mock
import pygame

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
    # Reset the alien's bullet list and prev_time
    alien_instance.bullets = []
    alien_instance.prev_time = 0
    
    # First call - should NOT shoot because curr_time - prev_time (0-0) < 500
    with patch('pygame.time.get_ticks', return_value=0):
        alien_instance.shoot_alien_bullets(player_instance, 0.1)
    assert len(alien_instance.bullets) == 0, "First call should NOT add a bullet (0-0 < 500)"
    
    # Set prev_time to a known value (0)
    alien_instance.prev_time = 0
    
    # Second call - should shoot because curr_time (600) - prev_time (0) >= 500
    with patch('pygame.time.get_ticks', return_value=600):
        alien_instance.shoot_alien_bullets(player_instance, 0.1)
    
    # Should have 1 bullet now
    assert len(alien_instance.bullets) == 1, "Second call should add first bullet (600-0 >= 500)"
    bullet = alien_instance.bullets[0]
    assert bullet.color == (255, 100, 255)  # Hardcoded color in alien.py
    
    # Third call - should NOT shoot because not enough time has passed (only 100ms)
    with patch('pygame.time.get_ticks', return_value=700):
        alien_instance.shoot_alien_bullets(player_instance, 0.1)
    assert len(alien_instance.bullets) == 1, "Third call should NOT add a bullet (700-600 < 500)"
    
    # Fourth call - should shoot because 500ms has passed since last shot
    with patch('pygame.time.get_ticks', return_value=1200):
        alien_instance.shoot_alien_bullets(player_instance, 0.1)
    
    # Should now have 2 bullets
    assert len(alien_instance.bullets) == 2, "Fourth call should add second bullet (1200-600 >= 500)"
    
    # Verify the second bullet's velocity direction is towards the player
    bullet2 = alien_instance.bullets[1]
    direction_to_player = (player_instance.pos - alien_instance.pos).normalize()
    
    # Create a vector from the bullet's velocity components
    bullet_direction = pygame.Vector2(bullet2.dx, bullet2.dy).normalize()
    assert abs(bullet_direction.x + direction_to_player.x) < 0.1, f"Bullet X direction {bullet_direction.x} should point towards player {direction_to_player.x}"
    assert abs(bullet_direction.y - direction_to_player.y) < 0.1, f"Bullet Y direction {bullet_direction.y} should point towards player {direction_to_player.y}"