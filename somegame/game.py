import pygame

from somegame.player import Player
from somegame.student_me import StudentME
from somegame.util import load_texture


class GameExited(BaseException):
    pass


class Game(object):
    __slots__ = ['sprites', 'surface', 'clock', 'fps', 'player']

    def __init__(self):
        self.sprites = pygame.sprite.Group()
        self.fps = 60

    def run(self):
        pygame.display.set_mode((800, 600))
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.init()
        try:
            while True:
                millisecs = self.clock.tick(self.fps)
                secs = millisecs / 1000.0
                self.draw()
                self.update(secs)
                self.process_events()
        except GameExited:
            return

    def init(self):
        self.player = Player(game=self, position=self.to_absolute_position(0.5, 0.5))
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
        pygame.display.flip()

    def to_absolute_position(self, rx, ry):
        width, height = self.surface.get_size()
        return (rx * width, ry * height)
