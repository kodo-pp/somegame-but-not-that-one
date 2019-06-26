import abc

from somegame.util import SpriteBase, Vector2D


class Mob(SpriteBase):
    def __init__(self, game, position):
        super().__init__(game=game)
        self.momentum = Vector2D(0.0, 0.0)
        self.position = position
    
    def update(self, time_interval):
        self.ai(time_interval)
        self.move_by(*(self.momentum * time_interval).to_tuple())
        self.update_rect()

    @abc.abstractmethod
    def ai(self, time_interval):
        pass

    def move_to(self, x, y):
        if self.prevent_collisions:
            blocker = self.game.get_position_blocker((x, y), self.hit_radius, self)
            if blocker is not None:
                vec = Vector2D(x, y) - Vector2D(*blocker.position)
                vec.stretch(5000.0)
                self.momentum += vec
                blocker.momentum -= vec
        super().move_to(x, y)

    def collides_with(self, sprite, radius):
        my_position = Vector2D(*self.position)
        sprite_position = Vector2D(*sprite.position)
        distance_sq = (sprite_position - my_position).length_sq()
        return distance_sq <= (radius + sprite.hit_radius) ** 2

    acceleration = 1000.0
    attack_radius = 0.0
    friction = 1500.0
    hit_radius = 30.0
    prevent_collisions = True
    speed = 100.0
