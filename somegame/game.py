import os

import pygame
import yaml
from loguru import logger

import somegame.powerup as powerup
from somegame.control_exceptions import *
from somegame.deadline import Deadline
from somegame.fps_osd import FpsOSD
from somegame.health_osd import HealthOSD
from somegame.ivr import IVR
from somegame.level_transition_overlay import LevelTransitionOverlay
from somegame.mob import Mob
from somegame.not_a_flower import NotAFlower
from somegame.player import Player
from somegame.student_me import StudentME
from somegame.util import load_texture, Vector2D, probability_choose


class LevelLoadError(RuntimeError):
    pass


entities = {
    'student_me': StudentME,
    'deadline': Deadline,
    'not_a_flower': NotAFlower,
    'ivr': IVR,
}


powerup_list = [
    (powerup.HealthUp, 1.0),
    (powerup.FireRateUp, 1.0),
    (powerup.SpeedUp, 1.0),
    (powerup.MaxHP, 0.3),
]


class Game(object):
    __slots__ = [
        'average_fps',
        'clock',
        'death_overlay_image',
        'enemies',
        'fps',
        'fps_osd',
        'frame_counter',
        'has_player_died',
        'health_osd',
        'is_showing_level_overlay',
        'level_name',
        'level_transition_overlay',
        'mobs',
        'player',
        'sprite_removal_queue',
        'sprites',
        'surface',
        'time_counter',
    ]

    def __init__(self):
        self.sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.fps = 60
        self.frame_counter = 0
        self.time_counter = 0.0
        self.average_fps = None
        self.sprite_removal_queue = []
        self.is_showing_level_overlay = False
        self.level_name = None
        self.player = None
        self.has_player_died = False

    def run(self):
        logger.info('Initializing Pygame-related objects')
        pygame.display.set_mode((800, 600))
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.init()
        logger.info('Entering main loop')
        try:
            while True:
                try:
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
                    if not self.is_showing_level_overlay and self.should_switch_level():
                        self.load_level(self.get_next_level_name(), reward=self.get_random_powerup())
                except PlayerDied as e:
                    logger.info('Player died')
                    self.fps = 5
                    self.has_player_died = True
                    self.death_overlay_image = self.surface.copy()
                    texture = load_texture('death_screen.png', root='assets/overlays').convert(24)
                    texture.set_alpha(200)
                    self.death_overlay_image.blit(texture, (0, 0))
        except GameExited:
            logger.info('Game exited')
            return

    def init(self):
        logger.info('Running initialization routines')
        self.fps_osd = FpsOSD(game=self)
        self.load_level(os.getenv('SOMEGAME_START_LEVEL', '0'))

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

    def add_sprite(self, sprite, enemy=False):
        logger.debug('Adding sprite of class `{}` with hexid {}', sprite.__class__.__name__, hex(id(sprite)))
        self.sprites.add(sprite)
        if isinstance(sprite, Mob):
            self.mobs.add(sprite)
        if enemy:
            self.enemies.add(sprite)

    def enqueue_sprite_removal(self, sprite):
        self.sprite_removal_queue.append(sprite)

    def get_next_level_name(self):
        return str(int(self.level_name) + 1)

    @staticmethod
    def get_level_entry_overlay(level_name):
        try:
            return load_texture('overlay.png', root=os.path.join('assets', 'levels', level_name))
        except Exception as e:
            raise LevelLoadError(
                'Failed to load entry overlay image for level `{}`: {}'.format(level_name, str(e))
            ) from e

    @staticmethod
    def read_level(level_name):
        try:
            with open(os.path.join('assets', 'levels', level_name, 'level.yml')) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise LevelLoadError('Failed to read level `{}`: {}'.format(level_name, str(e))) from e

    def level_transition_finished(self):
        self.is_showing_level_overlay = False
        self.level_transition_overlay = None

    def should_switch_level(self):
        return len(self.enemies.sprites()) == 0

    def load_level(self, level_name, reward=None):
        logger.info('Loading level `{}`'.format(level_name))
        self.health_osd = None
        self.sprites.empty()
        self.mobs.empty()
        self.enemies.empty()
        if self.player is None:
            self.player = Player(game=self, position=self.surface.get_rect().center)
        self.level_name = level_name
        try:
            level = self.read_level(level_name)
            player_position_info = level['player']['position']
            #self.player = Player(
            #    game = self,
            #    position = self.to_absolute_position(player_position_info['x'], player_position_info['y']),
            #)
            self.player.position = self.to_absolute_position(player_position_info['x'], player_position_info['y'])
            self.add_sprite(self.player)
            for ent in level['entities']:
                name = ent['name']
                position = self.to_absolute_position(*ent['position'])
                if name not in entities:
                    raise LevelLoadError('Unknown entity name: `{}`'.format(name))
                Entity = entities[name]

                entity = Entity(game=self, position=position)
                if ent['is_enemy']:
                    self.enemies.add(entity)
                self.add_sprite(entity)
            self.is_showing_level_overlay = True
            self.level_transition_overlay = LevelTransitionOverlay(
                game = self,
                image = self.get_level_entry_overlay(level_name),
                powerup_image = None if reward is None else reward.image,
            )
            if reward is not None:
                reward.apply(self.player)
            self.level_transition_overlay.update(0.0)
            self.health_osd = HealthOSD(game=self)
        except Exception as e:
            raise LevelLoadError('Failed to load level `{}`: {}'.format(level_name, str(e))) from e

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise GameExited()

    def update(self, time_interval):
        if self.is_showing_level_overlay:
            self.level_transition_overlay.update(time_interval)
        elif not self.has_player_died:
            self.sprites.update(time_interval)
            for i in self.sprite_removal_queue:
                logger.debug('Removing sprite of class `{}` with hexid {}', i.__class__.__name__, hex(id(i)))
                i.kill()
            self.sprite_removal_queue = []
            self.fps_osd.update()
            self.health_osd.update()

    def draw(self):
        self.surface.fill(color=(0, 0, 0))
        if self.is_showing_level_overlay:
            self.surface.blit(self.level_transition_overlay.image, (0, 0))
        elif self.has_player_died:
            self.surface.blit(self.death_overlay_image, (0, 0))
        else:
            self.sprites.draw(self.surface)
            self.fps_osd.draw(self.surface)
            self.health_osd.draw(self.surface)
        pygame.display.flip()

    def to_absolute_position(self, rx, ry):
        width, height = self.surface.get_size()
        return (rx * width, ry * height)

    def get_average_fps(self):
        return self.average_fps

    def get_random_powerup(self):
        return probability_choose(powerup_list)(game=self)
