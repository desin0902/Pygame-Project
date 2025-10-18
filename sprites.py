import pygame
import config
from config import *
import math
import random
import time
from parents import AnimatedSprite, SpriteSheet, Block, DisplayText

class Player(AnimatedSprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER

        super().__init__(x, y, self.game.all_sprites, self.game.player)

        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        player_sprite = pygame.image.load(resource_path(SPRITE_PLAYER)).convert_alpha()
        sprite_sheet = SpriteSheet(player_sprite)

        animation_steps = [5, 5, 5, 1, 8]

        step_counter = 0

        for animation in animation_steps:
            temp_image_list = []
            for _ in range(animation):
                temp_image_list.append(sprite_sheet.get_image(step_counter, 32, 32))
                step_counter += 1
            self.animation_list.append(temp_image_list)

        #load player sprite
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(self.animation_list[self.action_state][self.frame], (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.dead = False

        pygame.mixer.init()
        self.jump_sound = pygame.mixer.Sound(resource_path(SOUND_JUMP))
        self.jump_sound.set_volume(VOL_JUMP)
        self.enemy_bounce = pygame.mixer.Sound(resource_path(SOUND_BOUNCE))
        self.enemy_bounce.set_volume(VOL_BOUNCE)

    def update(self):
        self.movement()
        self.animate()

        self.rect.x += self.x_change
        self.collision_detect('x')
        self.rect.y += self.y_change
        self.collision_detect('y')

        self.check_if_falling()

        self.apply_gravity()
        self.apply_friction()

    def movement(self):
        keys = pygame.key.get_pressed()
        moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or \
                keys[pygame.K_d] or keys[pygame.K_e] or keys[pygame.K_UP] or \
                (self.x_change != 0 and not self.action_state == PLAYER_JUMP)
        new_state = None

        if keys[pygame.K_UP] and self.grounded:
            self.y_change -= PLAYER_JUMP_SPEED
            self.grounded = False
            new_state = PLAYER_JUMP
            self.jump_sound.play()

        elif keys[pygame.K_RIGHT]:
            self.facing = 'right'
            self.x_change += self.accelerate(1)
            if not self.action_state == PLAYER_JUMP or self.grounded:
                new_state = PLAYER_RUN
        elif keys[pygame.K_LEFT]:
            self.facing = 'left'
            self.x_change -= self.accelerate(-1)
            if not self.action_state == PLAYER_JUMP or self.grounded:
                new_state = PLAYER_RUN

        # special animations
        elif keys[pygame.K_d]:
            if not self.action_state == PLAYER_JUMP or self.grounded:
                new_state = PLAYER_BLINK
        elif keys[pygame.K_e]:
            if not self.action_state == PLAYER_JUMP or self.grounded:
                new_state = PLAYER_WAG

        if self.grounded and not moving:
            new_state = PLAYER_IDLE

        if new_state is not None and new_state != self.action_state:
            self.set_action_state(new_state)

        # cap player speed
        if self.x_change > config.PLAYER_MAX_SPEED:
            self.x_change = config.PLAYER_MAX_SPEED
        elif self.x_change < -config.PLAYER_MAX_SPEED:
            self.x_change = -config.PLAYER_MAX_SPEED

        # short hop
        if not keys[pygame.K_UP] and self.y_change < 0:
            self.y_change *= SHORT_HOP_MOD

    def accelerate(self, direction):
        if self.x_change * direction >= 0:
            if self.grounded:
                return config.PLAYER_SPEED
            else:
                return config.PLAYER_SPEED * AIR_MOD

        normalized_speed = abs(self.x_change) / config.PLAYER_MAX_SPEED
        acceleration = config.PLAYER_SPEED * (1 - normalized_speed ** 0.5)
        if self.grounded:
            return config.PLAYER_SPEED
        else:
            return config.PLAYER_SPEED * AIR_MOD

    def apply_friction(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            return
        if self.x_change > 0 and self.grounded:
            self.x_change -= config.FRICTION
            if self.x_change < 0:
                self.x_change = 0
        elif self.x_change > 0 and not self.grounded:
            self.x_change -= config.FRICTION * config.AIR_RESISTANCE
            if self.x_change < 0:
                self.x_change = 0
        elif self.x_change < 0 and self.grounded:
            self.x_change += config.FRICTION
            if self.x_change > 0:
                self.x_change = 0
        elif self.x_change < 0 and not self.grounded:
            self.x_change += config.FRICTION * config.AIR_RESISTANCE
            if self.x_change > 0:
                self.x_change = 0

    def apply_gravity(self):
        if not self.grounded:
            if self.y_change > 0:
                self.y_change += config.GRAVITY * FAST_FALL_MOD
            else:
                self.y_change += config.GRAVITY
        else:
            self.y_change = 0

    def collision_detect(self, direction):
        super().collision_detect(direction)

        #Enemy collision
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemy, False)
        if enemy_hits:
            if direction == 'y' and self.y_change > 0:
                for hit in enemy_hits:
                    if hit.action_state != ENEMY_SMUSH:
                        hit.action_state = ENEMY_SMUSH
                        hit.animation_rate = ENEMY_DIE_SPEED
                        hit.move_state = 'stop'
                        hit.frame = 0
                        hit.last_update = pygame.time.get_ticks()

                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_UP]:
                            self.y_change = PLAYER_BOUNCE_SPEED
                        else:
                            self.y_change = PLAYER_BOUNCE_SPEED / 2
                        self.grounded = False

                        # change animation to jump
                        self.set_action_state(PLAYER_JUMP)

                        # increase score
                        self.game.score.increase_score(ENEMY_DIE_POINTS)

                        self.enemy_bounce.play()
            else:
                for hit in enemy_hits:
                    if hit.action_state != ENEMY_SMUSH and not self.dead:
                        self.die()

        # fell off the map
        if self.rect.top >= 480:
            self.die()

        # game win
        if pygame.sprite.spritecollide(self, self.game.flag, False):
            self.game.score.increase_score(LEVEL_WIN_POINTS)
            self.game.next_level()

    def die(self):
        self.action_state = PLAYER_DEATH
        self.frame = 0
        self.y_change = 0
        self.x_change = 0
        self.dead = True
        self.game.lives.lose_life()


class Block1(Block):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, SPRITE_BRICK_1, game.all_sprites, game.blocks)


class Block2(Block):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, SPRITE_BRICK_2, game.all_sprites, game.blocks)


class Flag(Block):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, SPRITE_FLAG, game.all_sprites, game.flag)


class Enemy(AnimatedSprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        super().__init__(x, y, self.game.all_sprites, self.game.enemy)

        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT

        self.wasOnScreen = False

        enemy_sprite = pygame.image.load(resource_path(SPRITE_ENEMY_1)).convert_alpha()
        sprite_sheet = SpriteSheet(enemy_sprite)

        animation_steps = [4, 5]

        self.action_state = ENEMY_WALK

        step_counter = 0

        for animation in animation_steps:
            temp_image_list = []
            for _ in range(animation):
                temp_image_list.append(sprite_sheet.get_image(step_counter, self.width, self.height))
                step_counter += 1
            self.animation_list.append(temp_image_list)

        #load enemy sprite
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(self.animation_list[self.action_state][self.frame], (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


    def update(self):
        if self.is_on_screen or self.wasOnScreen:
            self.wasOnScreen = True
            self.movement()
            self.animate()

            # remove enemy once death animation completes
            if self.action_state == ENEMY_SMUSH and self.frame == len(self.animation_list[1]) - 1:
                self.kill()

            self.rect.x += self.x_change
            self.collision_detect('x')
            self.rect.y += self.y_change
            self.collision_detect('y')

            self.check_if_falling()

            #enemy gravity
            if not self.grounded:
                self.y_change += config.GRAVITY
            else:
                self.y_change = 0


    @property
    def is_on_screen(self):
        return self.rect.colliderect(self.game.camera.get_world_rect())


    def movement(self):
        if self.move_state == 'left':
            self.x_change = -1
        elif self.move_state == 'right':
            self.x_change = 1
        else:
            self.x_change = 0



