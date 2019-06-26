from somegame.mob import Mob
from somegame.util import load_texture, Vector2D


class StudentME(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.image = load_texture('s_me/main.png')
        self.update_rect()

    def ai(self, time_interval):
        target_point = Vector2D(*self.game.player.position)
        source_point = Vector2D(*self.position)

        desired_vector = target_point - source_point
        desired_length = desired_vector.length()
        direction_vector = desired_vector.normalized()
        max_length = time_interval * self.speed
        resulting_vector = direction_vector * min(desired_length, max_length)
        self.momentum += resulting_vector.stretched(self.acceleration * time_interval)
        self.momentum.chomp(self.speed)

        #resulting_point = source_point + resulting_vector
        #self.move_to(resulting_point.x, resulting_point.y)

        if self.collides_with(self.game.player, radius=self.attack_radius):
            self.game.player.hit_by(self, vector=direction_vector, force=self.attack_knockback)

    speed = 100.0
    attack_radius = 20.0
    attack_knockback = 400.0
