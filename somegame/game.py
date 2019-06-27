import os

import pygame
import yaml
from loguru import logger

from somegame.control_exceptions import *
from somegame.fps_osd import FpsOSD
from somegame.health_osd import HealthOSD
from somegame.mob import Mob
from somegame.player import Player
from somegame.student_me import StudentME
from somegame.util import load_texture, Vector2D


class LevelLoadError(RuntimeError):
    pass


entities = {
    'student_me': StudentME,
}


class Game(object):
    __slots__ = [
        'ai_mobs',
        'average_fps',
        'clock',
        'fps',
        'fps_osd',
        'frame_counter',
        'health_osd',
        'player',
        'sprite_removal_queue',
        'sprites',
        'surface',
        'time_counter',
    ]

    def __init__(self):
        self.sprites = pygame.sprite.Group()
        self.ai_mobs = pygame.sprite.Group()
        self.fps = 60
        self.frame_counter = 0
        self.time_counter = 0.0
        self.average_fps = None
        self.sprite_removal_queue = []

    def run(self):
        logger.info('Initializing Pygame-related objects')
        pygame.display.set_mode((800, 600))
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.init()
        logger.info('Entering main loop')
        try:
            try:
                while True:
                    millisecs = self.clock.tick(self.fps)
                    secs = millisecs / 1000.0
                    self.draw()
                    self.update(secs)
                    self.process_events()
                    self.frame_counter += 1
                    self.time_counter += secs
                    if self.frame_counter >= 10:
                        self.average_fps = self.frame_counter / self.time_counter
                        self.frame_counter = 0
                        self.time_counter = 0
            except PlayerDied as e:
                logger.info('Player died')
                raise GameExited() from e
        except GameExited:
            logger.info('Game exited')
            return

    def init(self):
        logger.info('Running initialization routines')
        self.fps_osd = FpsOSD(game=self)
        self.load_level('test')

    def get_position_blocker(self, position, radius, mob):
        point = Vector2D(*position)
        for sprite in self.sprites:
            if sprite is mob:
                continue
            if not sprite.trait_collides:
                continue
            sprite_point = Vector2D(*sprite.position)
            distance_sq = (sprite_point - point).length_sq()
            if distance_sq <= (radius + sprite.trait_hit_radius)**2:
                return sprite
        return None

    def add_sprite(self, sprite):
        logger.debug('Adding sprite of class `{}` with hexid {}', sprite.__class__.__name__, hex(id(sprite)))
        self.sprites.add(sprite)
        if isinstance(sprite, Mob):
            self.ai_mobs.add(sprite)

    def enqueue_sprite_removal(self, sprite):
        self.sprite_removal_queue.append(sprite)

    def load_level(self, level_name):
        logger.info('Loading level `{}`'.format(level_name))
        self.health_osd = None
        self.player = None
        self.sprites.empty()
        self.ai_mobs.empty()
        try:
            with open(os.path.join('assets', 'levels', level_name, 'level.yml')) as f:
                level = yaml.safe_load(f)
            player_position_info = level['player']['position']
            self.player = Player(
                game = self,
                position = self.to_absolute_position(player_position_info['x'], player_position_info['y']),
            )
            self.sprites.add(self.player)
            for ent in level['entities']:
                name = ent['name']
                position = self.to_absolute_position(*ent['position'])
                if name not in entities:
                    raise LevelLoadError('Unknown entity name: `{}`'.format(name))
                Entity = entities[name]

                ent = Entity(game=self, position=position)
                self.sprites.add(ent)
                self.ai_mobs.add(ent)
        except Exception as e:
            raise LevelLoadError('Failed to load level `{}`: {}'.format(level_name, str(e))) from e
        self.health_osd = HealthOSD(game=self)
        self.health_osd.draw(self.surface)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise GameExited()

    def update(self, time_interval):
        self.sprites.update(time_interval)
        for i in self.sprite_removal_queue:
            logger.debug('Removing sprite of class `{}` with hexid {}', i.__class__.__name__, hex(id(i)))
            i.kill()
        self.sprite_removal_queue = []
        self.fps_osd.update()
        self.health_osd.update()

    def draw(self):
        self.surface.fill(color=(0, 0, 0))
        self.sprites.draw(self.surface)
        self.fps_osd.draw(self.surface)
        self.health_osd.draw(self.surface)
        pygame.display.flip()

    def to_absolute_position(self, rx, ry):
        width, height = self.surface.get_size()
        return (rx * width, ry * height)

    def get_average_fps(self):
        return self.average_fps
