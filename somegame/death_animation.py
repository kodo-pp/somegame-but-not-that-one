import math
import pygame

from somegame.util import random_between, SpriteBase, Vector2D


class Particle(SpriteBase):
    def __init__(self, game, position, texture, clip, bottom, lifetime, momentum):
        super().__init__(game)
        self.image = texture.subsurface(clip)
        #self.image = pygame.Surface((5, 5), depth=32)
        #self.image.fill((100, 0, 0, 255))
        #self.image.set_clip(clip)
        self.bottom = bottom
        self.lifetime = lifetime
        self.momentum = momentum
        self.position = position
        self.update_rect()
        self.total_time = 0.0

    def update(self, time_interval):
        self.total_time += time_interval
        if self.total_time > self.lifetime:
            self.die()
            return
        self.momentum.y += self.trait_gravity * time_interval
        x, y = self.position
        x += self.momentum.x * time_interval
        y += self.momentum.y * time_interval
        y = min(y, self.bottom)
        self.position = x, y
        self.update_rect()

    trait_gravity = 725.0
    trait_bounds_checked = False
    trait_collides = False


class DeathAnimation(SpriteBase):
    def __init__(self, game, sprite):
        super().__init__(game)
        self.sprite = sprite

    def show(self):
        texture = self.sprite.image
        rect = self.sprite.rect
        width, height = rect.size
        block_size = 5
        x_count = (width + block_size - 1) // block_size
        y_count = (height + block_size - 1) // block_size
        for x in range(x_count):
            for y in range(y_count):
                position = (Vector2D(*rect.topleft) + Vector2D(x * block_size, y * block_size)).to_tuple()
                clip = rect.copy()
                clip.width = block_size
                clip.height = block_size
                clip.topleft = (x * block_size, y * block_size)
                speed = random_between(250.0, 300.0)
                rang = math.pi / 12
                angle = random_between(math.pi / 2 - rang, math.pi / 2 + rang)
                direction = Vector2D(math.cos(angle), -math.sin(angle))
                momentum = direction * speed
                lifetime = random_between(0.6, 1.0)
                bottom = rect.bottom + random_between(-10.0, 10.0)
                particle = Particle(
                    game = self.game,
                    texture = texture,
                    position = position,
                    clip = clip,
                    bottom = bottom,
                    lifetime = lifetime,
                    momentum = momentum,
                )
                self.game.add_sprite(particle)
