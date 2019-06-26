import math
import os

import pygame


class Vector2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, v):
        return Vector2D(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Vector2D(self.x - v.x, self.y - v.y)

    def __mul__(self, k):
        return Vector2D(self.x * k, self.y * k)

    def __truediv__(self, k):
        return self * (1.0/k)

    def to_tuple(self):
        return (self.x, self.y)

    def length(self):
        return math.sqrt(self.length_sq())

    def length_sq(self):
        return self.x ** 2 + self.y ** 2

    def normalized(self):
        if self.length_sq() == 0.0:
            return self
        return self / self.length()


class SpriteBase(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.position = (0.0, 0.0)
    
    def update_rect(self):
        x, y = self.position
        rect = self.image.get_rect()
        rect.center = (round(x), round(y))
        self.rect = rect

    def move_by(self, dx, dy):
        x, y = self.position
        self.move_to(x + dx, y + dy)

    def move_to(self, x, y):
        width, height = self.game.surface.get_size()
        if x >= width:
            x = width
        if y >= height:
            y = height
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        self.position = x, y


def load_texture(name):
    return pygame.image.load(os.path.join('assets', 'textures', name))


def get_random_direction():
    ang = rd.random() * 2 * math.pi
    return Vector2D(math.sin(ang), math.cos(ang))
