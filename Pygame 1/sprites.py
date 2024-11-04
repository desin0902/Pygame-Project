import pygame
from config import *
import math
import random
import time
import spritesheet

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.player
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.x_change = 0
        self.y_change = 0
        self.grounded = True

        player_sprite = pygame.image.load("img/single.png").convert_alpha()
        sprite_sheet = spritesheet.SpriteSheet(player_sprite)

        #segment different animations on sprite sheet
        self.animation_list = []
        animation_steps = [5, 5, 5, 1, 8]

        #selects animation to play
        self.action_state = 0
        self.last_update = pygame.time.get_ticks()

        #sets speed of animation
        self.animation_rate = 250
        self.frame = 0
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

        pygame.mixer.init()
        self.jump_sound = pygame.mixer.Sound("sounds/jumping.wav")
        self.jump_sound.set_volume(.2)
        self.enemy_bounce = pygame.mixer.Sound("sounds/enemy-bounce.mp3")
        self.enemy_bounce.set_volume(.3)

    def update(self):
        self.movement()
        self.animate()

        self.rect.x += self.x_change
        self.collision_detect('x')
        self.rect.y += self.y_change
        self.collision_detect('y')

        self.check_if_falling()

        #player gravity
        if not self.grounded:
            self.y_change += GRAVITY
        else:
            self.y_change = 0

        #apply friction
        keys = pygame.key.get_pressed()
        if self.x_change > 0 and self.grounded and not keys[pygame.K_RIGHT]:
            self.x_change -= FRICTION
            if self.x_change < 0:
                self.x_change = 0
        elif self.x_change > 0 and not self.grounded and not keys[pygame.K_RIGHT]:
            self.x_change -= FRICTION / 2
            if self.x_change < 0:
                self.x_change = 0
        elif self.x_change < 0 and self.grounded and not keys[pygame.K_LEFT]:
            self.x_change += FRICTION
            if self.x_change > 0:
                self.x_change = 0
        elif self.x_change < 0 and not self.grounded and not keys[pygame.K_LEFT]:
            self.x_change += FRICTION / 2
            if self.x_change > 0:
                self.x_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'

            #Changes animation based on player movement
            if not self.action_state == 3:
                self.action_state = 2

        if keys[pygame.K_d]:
            if not self.action_state == 3:
                self.action_state = 1

        if keys[pygame.K_e]:
            if not self.action_state == 3:
                self.action_state = 4

        if keys[pygame.K_RIGHT]:
            self.x_change += PLAYER_SPEED

            #Changes animation based on player movement
            if not self.action_state == 3:
                self.action_state = 2

        #Jump
        if keys[pygame.K_UP] and self.grounded:
            self.y_change -= PLAYER_JUMP_SPEED
            self.grounded = False

            #change animation to jump
            self.action_state = 3

            #play sound effect
            self.jump_sound.play()

        #cap player speed
        if self.x_change > PLAYER_SPEED:
            self.x_change = PLAYER_SPEED
        elif self.x_change < -PLAYER_SPEED:
            self.x_change = -PLAYER_SPEED

    def animate(self):
        current_time = pygame.time.get_ticks()

        if self.frame >= len(self.animation_list[self.action_state]):
            self.frame = 0

        #Updates the frame once enough time has passed
        if current_time - self.last_update >= self.animation_rate:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.animation_list[self.action_state]):
                    self.frame = 0

        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(self.animation_list[self.action_state][self.frame], (0, 0))

    def collision_detect(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if direction == 'x':
            if hits:
                if self.x_change > 0:
                    self.rect.right = hits[0].rect.left
                elif self.x_change < 0:
                    self.rect.left = hits[0].rect.right
                self.x_change = 0
        elif direction == 'y':
            if hits:
                if self.y_change > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.grounded = True
                elif self.y_change < 0:
                    self.rect.top = hits[0].rect.bottom
                self.y_change = 0
            else:
                self.grounded = False

        #Enemy collision
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemy, False)
        if enemy_hits:
            if direction == 'y' and self.y_change > 0:
                for hit in enemy_hits:
                    if hit.action_state != 1:
                        hit.action_state = 1
                        hit.animation_rate = 75
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_UP]:
                            self.y_change = PLAYER_BOUNCE_SPEED
                        else:
                            self.y_change = PLAYER_BOUNCE_SPEED / 2
                        self.grounded = False

                        #change animation to jump
                        self.action_state = 3

                        self.enemy_bounce.play()
            else:
                for hit in enemy_hits:
                    if hit.action_state != 1:
                        self.game.win = False
                        self.game.playing = False

        #fell off the map
        if self.rect.top >= 480:
            self.game.win = False
            self.game.playing = False

        #game win
        if pygame.sprite.spritecollide(self, self.game.flag, False):
            self.game.win = True
            self.game.playing = False

    def check_if_falling(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if not hits:
            self.grounded = False
        else:
            self.grounded = True
            self.action_state = 0
        self.rect.y -= 1

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        block_sprite = pygame.image.load("img/Brick 1.png").convert_alpha()

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        #load player sprite
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(block_sprite, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Block2(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        block_sprite = pygame.image.load("img/Brick 2.png").convert_alpha()

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        #load player sprite
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(block_sprite, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Flag(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.flag
        pygame.sprite.Sprite.__init__(self, self.groups)
        flag_sprite = pygame.image.load("img/GameWinFlag.png").convert_alpha()

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        #load player sprite
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(flag_sprite, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemy
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT

        self.x_change = 0
        self.y_change = 0
        self.move_state = 'left'
        self.grounded = True
        self.wasOnScreen = False

        enemy_sprite = pygame.image.load("img/Mob1.png").convert_alpha()
        sprite_sheet = spritesheet.SpriteSheet(enemy_sprite)

        #segment different animations on sprite sheet
        self.animation_list = []
        animation_steps = [4, 5]


        #selects animation to play
        self.action_state = 0
        self.last_update = pygame.time.get_ticks()

        #sets speed of animation
        self.animation_rate = 250
        self.frame = 0
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
        if self.is_on_screen() or self.wasOnScreen:
            self.wasOnScreen = True
            self.movement()
            self.animate()

            #remove enemy once death animation completes
            if self.action_state == 1 and self.frame == len(self.animation_list[1]) - 1:
                self.kill()

            self.rect.x += self.x_change
            self.collision_detect('x')
            self.rect.y += self.y_change
            self.collision_detect('y')

            self.check_if_falling()

            #enemy gravity
            if not self.grounded:
                self.y_change += GRAVITY
            else:
                self.y_change = 0


    def is_on_screen(self):
        return self.rect.colliderect(self.game.camera.get_world_rect())


    def movement(self):
        if self.move_state == 'left':
            self.x_change = -1
        elif self.move_state == 'right':
            self.x_change = 1


    def animate(self):
        current_time = pygame.time.get_ticks()

        if self.frame >= len(self.animation_list[self.action_state]):
            self.frame = 0

        #Updates the frame once enough time has passed
        if current_time - self.last_update >= self.animation_rate:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.animation_list[self.action_state]):
                    self.frame = 0

        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(self.animation_list[self.action_state][self.frame], (0, 0))


    def collision_detect(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if direction == 'x':
            if hits:
                if self.x_change > 0:
                    self.rect.right = hits[0].rect.left
                    self.move_state = 'left'
                elif self.x_change < 0:
                    self.rect.left = hits[0].rect.right
                    self.move_state = 'right'
                self.x_change = 0
        elif direction == 'y':
            if hits:
                if self.y_change > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.grounded = True
                elif self.y_change < 0:
                    self.rect.top = hits[0].rect.bottom
                self.y_change = 0
            else:
                False


    def check_if_falling(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if not hits:
            self.grounded = False
        else:
            self.grounded = True
        self.rect.y -= 1

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(0, 0, WIN_WIDTH, WIN_HEIGHT)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        x = max(-(self.map_width - self.width), x)  # right
        y = min(0, y)  # top
        y = max(-(self.map_height - self.height), y)  # bottom

        self.camera = pygame.Rect(x, y, self.width, self.height)

    def get_world_rect(self):
        # enemy action range
        return pygame.Rect(-(self.camera.x - 60), self.camera.y, self.width, self.height)


class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize, scale_factor):
        self.fontsize = fontsize
        self.content = content

        self.initial_x = x
        self.initial_y = y
        self.initial_width = width
        self.initial_height = height
        self.scale_factor = scale_factor

        self.fg = fg
        self.bg = bg

        self.update_position(self.initial_x, self.initial_y, self.initial_width, self.initial_height, self.scale_factor)

        self.button_sound = pygame.mixer.Sound("sounds/menu-select.mp3")
        self.button_sound.set_volume(.4)

    def update_position(self, x, y, width, height, scale_factor):
        self.scale_factor = scale_factor

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.scaled_width = int(self.width * self.scale_factor)
        self.scaled_height = int(self.height * self.scale_factor)

        self.image = pygame.Surface((self.scaled_width, self.scaled_height))
        self.image.fill(self.bg)

        self.rect = self.image.get_rect(topleft=(self.x * self.scale_factor, self.y * self.scale_factor))

        scaled_fontsize = int(self.fontsize * self.scale_factor)
        self.font = pygame.font.Font('Cantarell.ttf', scaled_fontsize)
        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.scaled_width / 2, self.scaled_height / 2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                self.button_sound.play()
                return True
            return False
        return False
