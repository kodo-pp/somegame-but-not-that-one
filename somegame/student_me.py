from somegame.mob import Mob
from somegame.util import load_texture, Vector2D


class StudentME(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.main_texture = load_texture('s_me/main.png')
        self.hit_texture = load_texture('s_me/main.png')    # TODO: actually draw hit texture
        self.image = self.main_texture
        self.update_rect()

    def ai(self, time_interval):
        target_point = Vector2D(*self.game.player.position)
        source_point = Vector2D(*self.position)

        desired_vector = target_point - source_point
        desired_length = desired_vector.length()
        direction_vector = desired_vector.normalized()
        max_length = time_interval * self.trait_speed
        resulting_vector = direction_vector * min(desired_length, max_length)
        self.momentum += resulting_vector.stretched(self.trait_acceleration * time_interval)
        self.momentum.chomp(self.speed)

        if self.collides_with(self.game.player, radius=self.trait_attack_radius):
            self.game.player.hit_by(self, vector=direction_vector, force=self.trait_attack_knockback, damage=1)

    trait_attack_knockback = 400.0
    trait_attack_radius = 20.0
    trait_death_animation_enabled = True
    trait_speed = 100.0
