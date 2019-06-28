import pygame
from loguru import logger

from somegame.osd import OSD


class FpsOSD(OSD):
    def __init__(self, game):
        super().__init__(game)
        logger.info('Loading font')
        self.font = pygame.font.Font(pygame.font.get_default_font(), 32)

    def draw(self, surface):
        fps = self.game.get_average_fps()
        fps_text = '<unknown>' if fps is None else '{:.1f}'.format(fps)
        tmp_surf = self.font.render('{} FPS'.format(fps_text), True, (255, 255, 255))
        surface.blit(tmp_surf, (0, 0))
