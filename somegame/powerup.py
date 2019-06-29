import abc
import random as rd

from loguru import logger

from somegame.item import Item
from somegame.util import load_texture


class Powerup(Item):
    def __init__(self, game):
        super().__init__(game)
        self.image = load_texture(self.trait_texture_filename)

    @abc.abstractmethod
    def apply(self, player):
        pass

    trait_texture_filename = None


class HealthUp(Powerup):
    def __init__(self, game):
        super().__init__(game)
        self.value = rd.choice([1, 2, 2, 3])

    def apply(self, player):
        logger.debug('HealthUp({})', self.value)
        player.heal(self.value)

    trait_texture_filename = 'powerups/health_up.png'


class MaxHP(Powerup):
    def __init__(self, game):
        super().__init__(game)

    def apply(self, player):
        logger.debug('MaxHP')
        player.hp = player.max_hp

    trait_texture_filename = 'powerups/max_hp.png'


class FireRateUp(Powerup):
    def __init__(self, game):
        super().__init__(game)
        self.value = rd.choice([0.6, 0.7, 0.8, 0.8])

    def apply(self, player):
        logger.debug('FireRateUp({})', self.value)
        player.weapon.cooldown_period *= self.value

    trait_texture_filename = 'powerups/fire_rate_up.png'


class SpeedUp(Powerup):
    def __init__(self, game):
        super().__init__(game)
        self.value = rd.choice([50, 100, 100, 100, 200])

    def apply(self, player):
        logger.debug('SpeedUp({})', self.value)
        player.speed += self.value

    trait_texture_filename = 'powerups/speed_up.png'
