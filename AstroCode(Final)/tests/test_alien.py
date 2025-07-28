
from unittest.mock import patch, Mock
import pygame

import core.constants as constants
from tests.mocks.pygame_mock import MockVector2
import random
from tests.te5t_cases import player_alien_pos


def test_alien_initialization(alien_instance):
    assert alien_instance.pos.x == 230
    assert alien_instance.pos.y == 230
    assert alien_instance.name == "Alien Type A"
    assert alien_instance.health == constants.ALIEN_MAX_HEALTH
    assert isinstance(alien_instance.pos, MockVector2)

def test_alien_take_damage(alien_instance, player_instance):
    alien_instance.health = constants.ALIEN_MAX_HEALTH
    initial_health_simulated = alien_instance.health
    with patch('core.constants.PLAYER_AWARENESS_RANGE', 200.0):
        for player_pos, alien_pos in player_alien_pos:
            alien_instance.pos = MockVector2(alien_pos[0], alien_pos[1])
            player_instance.pos = MockVector2(player_pos[0], player_pos[1])

            assert player_instance.pos.distance_to(alien_instance.pos) < constants.PLAYER_AWARENESS_RANGE

            direction = (alien_instance.pos - player_instance.pos).normalize()
            player_instance.shoot_bullet(
                bullet_type="Alien Type A",
                direction=direction,
                color=None
            )
            assert len(player_instance.bullets) == 1
            bullet = player_instance.bullets[0]
            assert bullet.active

            dt = 0.01
            while player_instance.bullet_index <= 0:
                player_instance.update_bullets([alien_instance], 0, dt)

            expected_health = initial_health_simulated - constants.DAMAGE_PER_HIT
            assert alien_instance.health == expected_health, \
                f"Expected alien health to be {expected_health} after taking damage, but got {alien_instance.health}"
            alien_instance.health = constants.ALIEN_MAX_HEALTH
            player_instance.bullet_index = 0

def test_alien_shoot_at_player(alien_instance, player_instance, monkeypatch):
    alien_instance.bullets = []
    alien_instance.prev_time = 0
    
    alien_instance.prev_time = 0
    
    with patch('pygame.time.get_ticks', return_value=0):
        alien_instance.shoot_at_player(player_instance, 0)
    assert len(alien_instance.bullets) == 0, "First call should NOT add a bullet (0-0 < 1000)"
    
    with patch('pygame.time.get_ticks', return_value=1100):
        alien_instance.shoot_at_player(player_instance, 0)
    
    assert len(alien_instance.bullets) == 1, f"Second call should add first bullet (1100-0 >= 1000), but found {len(alien_instance.bullets)} bullets"
    bullet = alien_instance.bullets[0]
    assert bullet.color == (255, 0, 0)
    
    with patch('pygame.time.get_ticks', return_value=1200):
        alien_instance.shoot_at_player(player_instance, 0)
    assert len(alien_instance.bullets) == 1, f"Third call should NOT add a bullet (1200-1100 < 1000), but found {len(alien_instance.bullets)} bullets"
    
    
    with patch('pygame.time.get_ticks', return_value=2300):
        alien_instance.shoot_at_player(player_instance, 0)
    
    assert len(alien_instance.bullets) == 2, f"Fourth call should add second bullet (2300-1100 >= 1000), but only found {len(alien_instance.bullets)} bullets"
    
    bullet2 = alien_instance.bullets[1]
    direction_to_player = (player_instance.pos - alien_instance.pos).normalize()
    
    bullet_direction = pygame.Vector2(bullet2.dx, bullet2.dy).normalize()
    
    assert abs(bullet_direction.x - direction_to_player.x) < 0.1, \
        f"Bullet X direction {bullet_direction.x} should match player direction {direction_to_player.x}"
    assert abs(bullet_direction.y - direction_to_player.y) < 0.1, \
        f"Bullet Y direction {bullet_direction.y} should match player direction {direction_to_player.y}"