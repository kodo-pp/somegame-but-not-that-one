import abc

from somegame.death_animation import DeathAnimation
from somegame.util import SpriteBase, Vector2D


class Mob(SpriteBase):
    def __init__(self, game, position):
        super().__init__(game=game)
        self.momentum = Vector2D(0.0, 0.0)
        self.position = position
        self.hit_timeout = 0.0
        self.control_disabled_for = 0.0
        self.main_texture = None
        self.hit_texture = None
        self.max_hp = self.trait_max_hp
        self.hp = self.max_hp
        self.speed = self.trait_speed
    
    def update(self, time_interval):
        self.ai(time_interval)

        if self.trait_physics_enabled:
            self.move_by(*(self.momentum * time_interval).to_tuple())
    
            # Friction
            self.momentum.stretch(max(0.0, self.momentum.length() - self.trait_friction * time_interval))

        # Update timeouts
        if self.hit_timeout > 0.0:
            self.hit_timeout -= time_interval
        if self.control_disabled_for > 0.0:
            self.control_disabled_for -= time_interval

        # Update textures
        if self.hit_timeout <= 0.0:
            self.image = self.main_texture
        self.update_rect()

    @abc.abstractmethod
    def ai(self, time_interval):
        pass

    def move_to(self, x, y):
        if self.trait_prevent_collisions and self.trait_physics_enabled:
            blocker = self.game.get_position_blocker((x, y), self.trait_hit_radius, self)
            if blocker is not None:
                vec = Vector2D(x, y) - Vector2D(*blocker.position)
                vec.stretch(500.0)
                self.momentum += vec
                blocker.momentum -= vec
        super().move_to(x, y)

    def collides_with(self, sprite, radius):
        my_position = Vector2D(*self.position)
        sprite_position = Vector2D(*sprite.position)
        distance_sq = (sprite_position - my_position).length_sq()
        return distance_sq <= (radius + sprite.trait_hit_radius) ** 2

    def disable_control_for(self, time):
        self.control_disabled_for = max(self.control_disabled_for, time)

    def is_control_enabled(self):
        return self.control_disabled_for <= 0.0

    def hit_by(self, attacker, vector, force, damage):
        if not self.is_hittable():
            return False
        if vector.length_sq() < 1e-9:
            vector = get_random_direction()
        self.inflict_damage(damage)
        vector = vector.normalized()
        self.momentum = vector * force
        self.disable_control_for(self.trait_hit_confusion_time)
        self.image = self.hit_texture
        self.hit_timeout = self.trait_hit_grace
        return True

    def die(self):
        if self.trait_death_animation_enabled:
            anim = DeathAnimation(game=self.game, sprite=self)
            anim.show()
        super().die()

    def inflict_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            self.die()

    def heal(self, hp):
        self.hp = min(self.max_hp, self.hp + hp)

    def is_hittable(self):
        return self.hit_timeout <= 0.0 and self.trait_is_hittable

    trait_acceleration = 1000.0
    trait_attack_radius = 0.0
    trait_death_animation_enabled = False
    trait_friction = 200.0
    trait_hit_confusion_time = 0.15
    trait_hit_grace = 0.2
    trait_hit_radius = 30.0
    trait_is_hittable = True
    trait_max_hp = 2
    trait_physics_enabled = True
    trait_prevent_collisions = True
    trait_speed = 100.0
