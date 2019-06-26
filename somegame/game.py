import pygame
from loguru import logger

from somegame.fps_osd import FpsOSD
from somegame.player import Player
from somegame.student_me import StudentME
from somegame.util import load_texture


class GameExited(BaseException):
    pass


class Game(object):
    __slots__ = [
        'sprites',
        'surface',
        'clock',
        'fps',
        'player',
        'frame_counter',
        'time_counter',
        'average_fps',
        'fps_osd',
    ]

    def __init__(self):
        self.sprites = pygame.sprite.Group()
        self.fps = 60
        self.frame_counter = 0
        self.time_counter = 0.0
        self.average_fps = None

    def run(self):
        logger.info('Initializing Pygame-related objects')
        pygame.display.set_mode((800, 600))
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.init()
        logger.info('Entering main loop')
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
        except GameExited:
            logger.info('Game exited')
            return

    def init(self):
        logger.info('Running initialization routines')
        self.player = Player(game=self, position=self.to_absolute_position(0.5, 0.5))
        self.fps_osd = FpsOSD(game=self)
        self.sprites.add(self.player)
        self.sprites.add(StudentME(game=self, position=self.to_absolute_position(0.3, 0.7)))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise GameExited()

    def update(self, time_interval):
        self.sprites.update(time_interval)

    def draw(self):
        self.surface.fill(color=(0, 0, 0))
        self.sprites.draw(self.surface)
        self.fps_osd.draw(self.surface)
        pygame.display.flip()

    def to_absolute_position(self, rx, ry):
        width, height = self.surface.get_size()
        return (rx * width, ry * height)

    def get_average_fps(self):
        return self.average_fps
