from somegame.mob import Mob
from somegame.util import load_texture, Vector2D


class NotAFlower(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.main_texture = load_texture('not_a_flower/main.png')
        self.hit_texture = load_texture('not_a_flower/hit.png')
        self.image = self.main_texture
        self.update_rect()
        self.movement_vector = Vector2D(1, 1).normalized() * self.speed

    def ai(self, time_interval):
        if self.is_on_edge('left') or self.is_on_edge('right'):
            self.movement_vector.x = -self.movement_vector.x
        if self.is_on_edge('top') or self.is_on_edge('bottom'):
            self.movement_vector.y = -self.movement_vector.y

        self.move_by(*(self.movement_vector * time_interval).to_tuple())

        if self.collides_with(self.game.player, radius=self.trait_attack_radius):
            self.game.player.hit_by(
                attacker = self,
                vector = self.movement_vector,
                force = self.trait_attack_knockback,
                damage = 2,
            )

    trait_attack_knockback = 400.0
    trait_attack_radius = 20.0
    trait_death_animation_enabled = True
    trait_max_hp = 10
    trait_physics_enabled = False
    trait_speed = 250.0
