import abc

from somegame.item import Item


class Weapon(Item):
    def __init__(self, game, holder):
        super().__init__(game)
        self.holder = holder
        self.cooldown_period = 1.0
        self.current_cooldown = 0.0

    @abc.abstractmethod
    def shoot(self, direction):
        pass

    def start_cooldown(self):
        self.current_cooldown = max(self.current_cooldown, self.cooldown_period)

    def is_on_cooldown(self):
        return self.current_cooldown > 0.0

    def update(self, time_interval):
        if self.current_cooldown > 0.0:
            self.current_cooldown -= time_interval
