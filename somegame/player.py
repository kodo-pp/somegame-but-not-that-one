import pygame
from loguru import logger

from somegame.control_exceptions import PlayerDied
from somegame.mob import Mob
from somegame.util import get_random_direction, load_texture, Vector2D


class Player(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.main_texture = load_texture('player/main.png')
        self.hit_texture = load_texture('player/hit.png')
        self.image = self.main_texture
        self.update_rect()
        self.hit_timeout = 0.0
        self.control_disabled_for = 0.0
        self.max_hp = 5
        self.hp = self.max_hp

    def ai(self, time_interval):
        # Friction
        self.momentum.stretch(max(0.0, self.momentum.length() - self.friction * time_interval))

        # Keyboard control
        if self.is_control_enabled():
            direction = Vector2D(*self.get_direction())
            self.momentum += direction * self.acceleration
            self.momentum.chomp(self.speed)

        # Movement
        self.move_by(*(self.momentum * time_interval).to_tuple())

        # Update timeouts
        if self.hit_timeout > 0.0:
            self.hit_timeout -= time_interval
        if self.control_disabled_for > 0.0:
            self.control_disabled_for -= time_interval

        # Update textures
        if self.hit_timeout <= 0.0:
            self.image = self.main_texture

    def is_hittable(self):
        return self.hit_timeout <= 0.0

    def inflict_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            raise PlayerDied()

    def hit_by(self, attacker, vector, force, damage):
        if not self.is_hittable():
            return False
        if vector.length_sq() < 1e-9:
            vector = get_random_direction()
        self.inflict_damage(damage)
        vector = vector.normalized()
        self.momentum = vector * force
        self.disable_control_for(self.hit_confusion_time)
        self.image = self.hit_texture
        self.hit_timeout = self.hit_grace
        logger.info('Player was hit! Remaining HP: {}/{}', self.hp, self.max_hp)
        return True

    def disable_control_for(self, time):
        self.control_disabled_for = max(self.control_disabled_for, time)

    def is_control_enabled(self):
        return self.control_disabled_for <= 0.0

    @staticmethod
    def get_direction():
        dir_x = 0
        dir_y = 0
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            dir_x -= 1
        if pressed_keys[pygame.K_RIGHT]:
            dir_x += 1
        if pressed_keys[pygame.K_UP]:
            dir_y -= 1
        if pressed_keys[pygame.K_DOWN]:
            dir_y += 1
        return dir_x, dir_y

    acceleration = 300.0
    collides = False
    hit_confusion_time = 0.25
    hit_grace = 0.4
    prevent_collisions = False
    speed = 200.0
