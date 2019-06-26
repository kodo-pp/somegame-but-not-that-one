import pygame

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
        self.momentum = Vector2D(0.0, 0.0)
        self.control_disabled_for = 0.0

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

    def hit_by(self, attacker, vector, force):
        if not self.is_hittable():
            return False
        if vector.length_sq() < 1e-9:
            vector = get_random_direction()
        vector = vector.normalized()
        self.momentum = vector * force
        self.disable_control_for(self.hit_confusion_time)
        self.image = self.hit_texture
        self.hit_timeout = self.hit_grace
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

    hit_grace = 0.45
    hit_confusion_time = 0.35
    acceleration = 300.0
    friction = 1500.0
    speed = 300.0
