import pygame
from loguru import logger

from somegame.game import Game


def main():
    logger.info('Initializing Pygame')
    pygame.init()
    logger.info('Initializing game core')
    game = Game()
    logger.info('Running game')
    game.run()
