import abc

from somegame.util import SpriteBase, Vector2D


class Mob(SpriteBase):
    def __init__(self, game, position):
        super().__init__(game=game)
        self.position = position
    
    def update(self, time_interval):
        self.ai(time_interval)
        self.update_rect()

    @abc.abstractmethod
    def ai(self, time_interval):
        pass

    def collides_with(self, sprite, radius):
        my_position = Vector2D(*self.position)
        sprite_position = Vector2D(*sprite.position)
        distance_sq = (sprite_position - my_position).length_sq()
        return distance_sq <= (radius + sprite.hit_radius)

    hit_radius = 40.0
    speed = 100.0
    attack_radius = 0.0


