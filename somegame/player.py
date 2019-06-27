import pygame
from loguru import logger

from somegame.control_exceptions import PlayerDied
from somegame.gun import Gun
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
        self.weapon = Gun(game=self.game, holder=self)

    def update(self, time_interval):
        super().update(time_interval)
        self.weapon.update(time_interval)

    def ai(self, time_interval):
        # Friction
        self.momentum.stretch(max(0.0, self.momentum.length() - self.trait_friction * time_interval))

        # Keyboard control
        if self.is_control_enabled():
            direction = Vector2D(*self.get_direction())
            self.momentum += direction * self.trait_acceleration
            self.momentum.chomp(self.trait_speed)
            self.maybe_shoot()

    def maybe_shoot(self):
        dir_x, dir_y = self.get_shot_direction()
        if dir_x == 0 and dir_y == 0:
            return False
        vector = Vector2D(dir_x, dir_y)
        self.weapon.shoot(vector)

    def die(self):
        raise PlayerDied()

    @staticmethod
    def get_direction():
        dir_x = 0
        dir_y = 0
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_a]:
            dir_x -= 1
        if pressed_keys[pygame.K_d]:
            dir_x += 1
        if pressed_keys[pygame.K_w]:
            dir_y -= 1
        if pressed_keys[pygame.K_s]:
            dir_y += 1
        return dir_x, dir_y

    @staticmethod
    def get_shot_direction():
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

    trait_acceleration = 300.0
    trait_collides = False
    trait_friction = 1500.0
    trait_hit_confusion_time = 0.25
    trait_hit_grace = 0.4
    trait_prevent_collisions = False
    trait_speed = 200.0
