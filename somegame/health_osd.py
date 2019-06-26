from pygame.sprite import Group

from somegame.osd import OSD
from somegame.util import load_texture, SpriteBase


class Heart(SpriteBase):
    def __init__(self, game, position):
        super().__init__(game)
        self.full_texture = load_texture('heart/full.png')
        self.empty_texture = load_texture('heart/empty.png')
        self._is_full = True
        self.position = position
        self.image = self.full_texture
        self.update_rect()

    def is_full(self):
        return self._is_full

    def set_full(self, value):
        self._is_full = value
        self.image = self.full_texture if value else self.empty_texture


class HealthOSD(OSD):
    def __init__(self, game):
        super().__init__(game)

        # XXX: Quite an ugly way to determine the size of one heart
        tmp = Heart(game=game, position=(0, 0))
        width, height = tmp.rect.size
        del tmp

        self.heart_list = [
            Heart(game=game, position=self.get_heart_position(i, width, height))
            for i in range(game.player.max_hp)
        ]
        self.hearts = Group(self.heart_list)

    def draw(self, surface):
        self.hearts.draw(surface)

    def update(self):
        hp = self.game.player.hp
        max_hp = self.game.player.max_hp
        assert len(self.heart_list) == max_hp       # TODO: dynamically change the number of hearts
        for i in range(max_hp):
            self.heart_list[-1-i].set_full(i < hp)

    def get_heart_position(self, heart_number, width, height):
        y = (height + 1) // 2
        x = self.game.surface.get_rect().right - (width + 1) // 2 - heart_number * width
        return x, y
