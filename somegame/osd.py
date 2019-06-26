import abc


class OSD(object):
    def __init__(self, game):
        self.game = game

    @abc.abstractmethod
    def draw(self, surface):
        pass

    def update(self):
        pass
