import pygame

from somegame.mob import Mob
from somegame.util import get_random_direction, load_texture


class Player(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.main_texture = load_texture('player/main.png')
        self.hit_texture = load_texture('player/hit.png')
        self.image = self.main_texture
        self.update_rect()
        self.hit_timeout = 0.0
        
    def ai(self, time_interval):
        dir_x, dir_y = self.get_direction()
        dx = dir_x * self.speed * time_interval
        dy = dir_y * self.speed * time_interval
        self.move_by(dx, dy)
        if self.hit_timeout > 0.0:
            self.hit_timeout -= time_interval
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
        self.move_by(*(vector * force).to_tuple())
        self.image = self.hit_texture
        self.hit_timeout = self.hit_grace
        return True

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

    hit_grace = 1.0
