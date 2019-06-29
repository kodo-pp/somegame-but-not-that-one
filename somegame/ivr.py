import random as rd

from somegame.deadline import Deadline
from somegame.gun import Gun, Bullet
from somegame.mob import Mob
from somegame.student_me import StudentME
from somegame.util import load_texture, Vector2D


class IVRBullet(Bullet):
    def should_hit(self, sprite):
        return sprite is self.game.player

    trait_speed = 400.0


class IVR(Mob):
    def __init__(self, game, position):
        super().__init__(game, position)
        self.main_texture = load_texture('ivr/main.png')
        self.hit_texture = load_texture('ivr/hit.png')
        self.image = self.main_texture
        self.weapon = Gun(
            game = game,
            holder = self,
            BulletClass = IVRBullet,
            cooldown_period = 0,
        )
        self.update_rect()
        self.before_attack = 5.0

    def attack1(self):
        x, y = self.position
        self.weapon.shoot(direction=Vector2D( 0,  1), cooldown=False, force_position=(x-20, y))
        self.weapon.shoot(direction=Vector2D( 0,  1), cooldown=False, force_position=(x,    y))
        self.weapon.shoot(direction=Vector2D( 0,  1), cooldown=False, force_position=(x+20, y))
        self.weapon.shoot(direction=Vector2D( 0, -1), cooldown=False, force_position=(x-20, y))
        self.weapon.shoot(direction=Vector2D( 0, -1), cooldown=False, force_position=(x,    y))
        self.weapon.shoot(direction=Vector2D( 0, -1), cooldown=False, force_position=(x+20, y))

        self.weapon.shoot(direction=Vector2D( 1,  0), cooldown=False, force_position=(x, y-20))
        self.weapon.shoot(direction=Vector2D( 1,  0), cooldown=False, force_position=(x, y   ))
        self.weapon.shoot(direction=Vector2D( 1,  0), cooldown=False, force_position=(x, y+20))
        self.weapon.shoot(direction=Vector2D(-1,  0), cooldown=False, force_position=(x, y-20))
        self.weapon.shoot(direction=Vector2D(-1,  0), cooldown=False, force_position=(x, y   ))
        self.weapon.shoot(direction=Vector2D(-1,  0), cooldown=False, force_position=(x, y+20))

        posv = Vector2D(x, y)
        dirv = Vector2D(*self.game.player.position) - posv

        self.weapon.shoot(direction=dirv, cooldown=False, force_position=(x+20, y+20))
        self.weapon.shoot(direction=dirv, cooldown=False, force_position=(x+20, y-20))
        self.weapon.shoot(direction=dirv, cooldown=False, force_position=(x-20, y+20))
        self.weapon.shoot(direction=dirv, cooldown=False, force_position=(x-20, y-20))

    def attack2(self):
        x, y = self.position
        self.game.add_sprite(
            StudentME(game=self.game, position=(x+50, y+50)),
            enemy=True,
        )
        self.game.add_sprite(
            StudentME(game=self.game, position=(x-50, y-50)),
            enemy=True,
        )
        self.game.add_sprite(
            StudentME(game=self.game, position=(x-50, y+50)),
            enemy=True,
        )
        self.game.add_sprite(
            StudentME(game=self.game, position=(x+50, y-50)),
            enemy=True,
        )

    def attack3(self):
        x, y = self.position
        self.game.add_sprite(
            Deadline(game=self.game, position=(x+50, y+50)),
            enemy=True,
        )
        self.game.add_sprite(
            Deadline(game=self.game, position=(x-50, y-50)),
            enemy=True,
        )

    def ai(self, time_interval):
        self.before_attack -= time_interval
        if self.before_attack <= 0.0:
            self.before_attack = 5.0
            rd.choice([self.attack1, self.attack2, self.attack3])()

        if self.collides_with(self.game.player, radius=self.trait_attack_radius):
            self.game.player.hit_by(self, vector=Vector2D(0, 0), force=self.trait_attack_knockback, damage=2)

    trait_attack_knockback = 400.0
    trait_attack_radius = 45.0
    trait_death_animation_enabled = True
    trait_physics_enabled = False
    trait_fire_delay = 2.0
    trait_max_hp = 50
    trait_speed = 0.0
