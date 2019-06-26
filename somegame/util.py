import math
import os
import random as rd

import pygame
from loguru import logger


class Vector2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, v):
        return Vector2D(self.x + v.x, self.y + v.y)
    
    def __iadd__(self, v):
        self.x += v.x
        self.y += v.y
        return self

    def __sub__(self, v):
        return Vector2D(self.x - v.x, self.y - v.y)

    def __isub__(self, v):
        self.x -= v.x
        self.y -= v.y
        return self

    def __mul__(self, k):
        return Vector2D(self.x * k, self.y * k)

    def __imul__(self, k):
        self.x *= k
        self.y *= k
        return self

    def __truediv__(self, k):
        return self * (1.0/k)

    def __itruediv__(self, k):
        self.x /= k
        self.y /= k
        return self

    def __neg__(self):
        return self * (-1.0)

    def to_tuple(self):
        """ Convert vector to tuple """
        return (self.x, self.y)

    def length(self):
        """ Return length of the vector. Pretty slow """
        return math.sqrt(self.length_sq())

    def length_sq(self):
        """ Return squared length of the vector. Much faster than length() """
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        """ Make this vector be of length 1, preserving its direction
    
        Warning: if the vector has length 0, it will be unchanged
        """
        if self.length_sq() == 0.0:
            return self
        l = self.length()
        self /= l

    def normalized(self):
        """ Return a normalized copy of this vector, see normalize() """
        if self.length_sq() == 0.0:
            return self
        return self / self.length()

    def stretch(self, length):
        """ Make this vector be of specified length 
        
        Warning: result may be incorrect if the vector has length 0
        """
        self.normalize()
        self *= length

    def stretched(self, length):
        """ Return a stretched copy of this vector, see stretch() """
        return self.normalized() * length

    def chomp(self, length):
        """ If this vector is longer than specified treshold, it make it be of specified length """
        if self.length_sq() < length**2:
            return
        self.stretch(length)

    def chomped(self, length):
        """ Return a chomped copy of this vector, see chomp() """
        return self if self.length_sq() < length**2 else self.stretched(length)


class SpriteBase(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.position = (0.0, 0.0)
    
    def update_rect(self):
        """ Update pygame rectangle of the image bound to the sprite """
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

    collides = True


# XXX: Add a lock here when (if) multithreading will be used
_texture_cache = {}

def load_texture(name):
    logger.info('Loading texture `{}`', name)
    global _texture_cache
    if name in _texture_cache:
        logger.info('Texture `{}` - cached', name)
        return _texture_cache[name]
    texture = pygame.image.load(os.path.join('assets', 'textures', name))
    _texture_cache[name] = texture
    logger.info('Texture `{}` - loaded from file', name)
    return texture


def get_random_direction():
    ang = rd.random() * 2 * math.pi
    return Vector2D(math.sin(ang), math.cos(ang))


def optional(x, d):
    return d if x is None else x
