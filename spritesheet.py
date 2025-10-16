import pygame
from config import *

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.animation_list = []
        self.action_state = 0
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_rate = PLAYER_ANIMATION_SPEED
    
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

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    #animate spritesheet
    def get_image(self, frame, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        return image
