import math

from somegame.util import SpriteBase


class LevelTransitionOverlay(SpriteBase):
    def __init__(self, game, image, powerup_image=None):
        super().__init__(game)
        self.image = image.convert(24)
        if powerup_image is not None:
            rect = powerup_image.get_rect()
            rect.center = self.image.get_rect().center
            rect.top = 0
            self.image.blit(powerup_image, rect)
        self.time_elapsed = 0.0
        self.has_level_switched = False

    def update_rect(self):
        self.rect = self.game.surface.get_rect()

    def update(self, time_interval):
        self.time_elapsed += time_interval
        alpha = self.get_alpha(self.time_elapsed)
        if alpha is None:
            self.die()
            return
        self.image.set_alpha(alpha)
        self.has_level_switched = (self.time_elapsed > 1.0)

    def die(self):
        self.game.level_transition_finished()
    
    @staticmethod
    def get_alpha(time):
        # ^ alpha
        # |  ,------,    alpha = 255
        # | /        \
        # |/          \  alpha = 0
        # +--------------------------> time
        # 0s 1s    3s 4s

        # x in [0; 1)
        to_absolute_value = lambda x: math.floor(x * 256)

        if time < 1.0:
            return to_absolute_value(time)
        elif time <= 3.0:
            return 255
        elif time <= 4.0:
            return to_absolute_value(4.0 - time)
        return None
