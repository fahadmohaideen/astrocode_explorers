from levels.base_level import Level
from core.constants import FOR_LOOP_COLOR
import pygame
import copy
import os

pygame.init()
pygame.font.init()

class Level2(Level):
    def __init__(self, code_font, title_font, menu_font):
        super().__init__(code_font, title_font, menu_font)
        #self.curr_nearest_alien = None
        self.level_id = 2
        self.code_blocks = []
        #self.commands["for_loop"] = {"color": FOR_LOOP_COLOR, "text": "For Loop"}
        self.commands["if_statement"] = {"color": FOR_LOOP_COLOR, "text": "if"}
        self.var_dict.update({"Alien near": [False, None, None],
                            "Alien Type A": [False, None, None],
                            "Alien Type B": [False, None, None],
                            "Alien Type C": [False, None, None]})
        # In Level2.__init__():
        self.value_options = [
            "Alien Type A",  
            "Alien Type B",  
            "Alien Type C"  
        ]
        self.current_value_index = -1
        self.shoot_index = -1
        self.spawn_aliens(3)
        self.load_assets()
        super()._init_commands()

    def handle_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._process_command_clicks_recursive(mouse_pos, self.main_code)

        super().handle_events(event, mouse_pos)

    def update(self, dt, keys):
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= self.player.speed * dt
            self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += self.player.speed * dt
            self.moving = True
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= self.player.speed * dt
            self.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += self.player.speed * dt
            self.moving = True
        else:
            self.moving = False

        self.player.pos += movement

        self.var_dict["Alien near"][0] = False
        for alien in self.aliens:
            alien_near = self.player.pos.distance_to(alien.pos) < 200
            self.var_dict[alien.name][0] = alien_near
            self.var_dict[alien.name][1] = alien if alien_near else None
            if alien_near:
                self.var_dict["Alien near"][0] = True
                self.curr_nearest_alien = alien

        active_aliens = [alien for alien in self.aliens if alien.active]
        self.player.update_bullets(active_aliens, self.level_id, dt)



    def _process_command_clicks_recursive(self, mouse_pos, commands_list):
        for cmd in commands_list:
            if cmd.rect and cmd.rect.collidepoint(mouse_pos):
                if cmd.is_conditional():
                    var_box, op_box, val_box = cmd.var_box, cmd.op_box, cmd.val_box
                    var_box, op_box, val_box = cmd.var_box, cmd.op_box, cmd.val_box

                    if var_box.collidepoint(mouse_pos):
                        current_var = getattr(cmd, 'condition_var', None)
                        cmd.condition_var = self._cycle_value(current_var, self.var_dict)

                elif cmd.cmd_type == "shoot":
                    if cmd.shoot_bullet_type_box and cmd.shoot_bullet_type_box.collidepoint(mouse_pos):
                        self.current_value_index = (self.current_value_index + 1) % len(self.value_options)
                        cmd.shoot_bullet_type = copy.deepcopy(self.value_options[self.current_value_index])
                        return True

                elif cmd.is_loop():
                    if cmd.iter_box.collidepoint(mouse_pos):
                        self.editing_loop_cmd = cmd
                        cmd.editing_text = ""
                        return True
                    self.editing_loop_cmd = None


            if cmd.is_loop() or cmd.is_conditional() or cmd.cmd_type == "while_loop":
                if self._process_command_clicks_recursive(mouse_pos, cmd.nested_commands):
                    return True

        return False