import pygame
from config import *

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.animation_list = []
        self.action_state = 0
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_rate = PLAYER_ANIMATION_SPEED

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.move_state = 'left'
        self.grounded = True
    
    def set_action_state(self, new_state, new_rate=None):
        if self.action_state != new_state:
            self.action_state = new_state
            self.frame = 0
            self.last_update = pygame.time.get_ticks()
            if new_rate:
                self.animation_rate = new_rate

    def animate(self):
        current_time = pygame.time.get_ticks()

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
                self.grounded = False

    def check_if_falling(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if not hits:
            self.grounded = False
        else:
            self.grounded = True
        self.rect.y -= 1


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, sprite, *groups):
        super().__init__(*groups)

        self.game = game
        self._layer = BLOCK_LAYER

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        block_sprite = pygame.image.load(resource_path(sprite)).convert_alpha()

        #load sprite
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.blit(block_sprite, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    #animate spritesheet
    def get_image(self, frame, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        return image


class DisplayText():
    def __init__(self, x, y, width, height, fg, content, fontsize, scale_factor, bg=None):
        self.initial_x = x
        self.initial_y = y
        self.initial_width = width
        self.initial_height = height
        self.fontsize = fontsize
        self.content = content
        self.fg = fg
        self.bg = bg

        self.scale_factor = scale_factor

        self.update_position(self.scale_factor)

    def update_position(self, scale_factor):
        self.scale_factor = scale_factor

        self.x = int(self.initial_x * self.scale_factor)
        self.y = int(self.initial_y * self.scale_factor)
        self.width = int(self.initial_width * self.scale_factor)
        self.height = int(self.initial_height * self.scale_factor)

        self.image = pygame.Surface((self.width, self.height))
        if self.bg:
            self.image.fill(self.bg)

        scaled_fontsize = int(self.fontsize * self.scale_factor)
        self.font = pygame.font.Font(resource_path(MAIN_FONT), scaled_fontsize)
        self.text = self.font.render(self.content, True, self.fg)

        self.text_rect = self.text.get_rect(center=(self.width / 2, self.height / 2))
        self.image.blit(self.text, self.text_rect)

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
