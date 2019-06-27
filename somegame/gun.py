from somegame.mob import Mob
from somegame.util import load_texture
from somegame.weapon import Weapon


class Bullet(Mob):
    def __init__(self, game, position, direction):
        super().__init__(game, position)
        self.direction = direction.normalized()
        self.main_texture = load_texture('bullet/main.png')
        self.image = self.main_texture
        self.update_rect()

    def ai(self, time_interval):
        self.move_by(*(self.direction * self.trait_speed * time_interval).to_tuple())
        for mob in self.game.mobs:
            if mob is self:
                continue
            if self.collides_with(sprite=mob, radius=self.trait_attack_radius):
                mob.hit_by(attacker=self, vector=self.direction, force=self.trait_attack_knockback, damage=1)
                self.die()
                return
        if not self.is_on_screen():
            self.die()
            return
    
    trait_attack_knockback = 400.0
    trait_attack_radius = 5
    trait_bounds_checked = False
    trait_collides = False
    trait_is_hittable = False
    trait_physics_enabled = False
    trait_prevent_collisions = False
    trait_speed = 600.0


class Gun(Weapon):
    def __init__(self, game, holder):
        super().__init__(game, holder)
        self.cooldown_period = 0.5

    def shoot(self, direction):
        if self.is_on_cooldown():
            return
        position = self.holder.position
        # TODO: holder
        self.game.add_sprite(Bullet(game=self.game, position=position, direction=direction))
        self.start_cooldown()
