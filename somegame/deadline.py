from somegame.gun import Gun, Bullet
from somegame.mob import Mob
from somegame.util import load_texture, Vector2D


class DeadlineBullet(Bullet):
    def should_hit(self, sprite):
        return sprite is self.game.player

    trait_should_rotate = True
    trait_speed = 300.0
    trait_texture_filename = 'deadline/bullet.png'


class Deadline(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.main_texture = load_texture('deadline/main.png')
        self.hit_texture = load_texture('deadline/hit.png')
        self.image = self.main_texture
        self.weapon = Gun(
            game = game,
            holder = self,
            BulletClass = DeadlineBullet,
            cooldown_period = self.trait_fire_delay,
        )
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
        self.momentum.chomp(self.trait_speed)

        self.weapon.update(time_interval)
        self.weapon.shoot(direction=Vector2D( 1,  0), cooldown=False)
        self.weapon.shoot(direction=Vector2D( 0,  1), cooldown=False)
        self.weapon.shoot(direction=Vector2D(-1,  0), cooldown=False)
        self.weapon.shoot(direction=Vector2D( 0, -1), cooldown=True)

        if self.collides_with(self.game.player, radius=self.trait_attack_radius):
            self.game.player.hit_by(self, vector=direction_vector, force=self.trait_attack_knockback, damage=1)

    trait_attack_knockback = 400.0
    trait_attack_radius = 20.0
    trait_death_animation_enabled = True
    trait_fire_delay = 2.0
    trait_max_hp = 5
    trait_speed = 50.0
