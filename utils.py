import pygame
import config
from config import *
from parents import DisplayText

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


class Button(DisplayText):
    def __init__(self, x, y, width, height, fg, bg, content, fontsize, scale_factor):
        super().__init__(x, y, width, height, fg, content, fontsize, scale_factor, bg=bg)

        self.button_sound = pygame.mixer.Sound(resource_path(SOUND_MENU_SELECT))
        self.button_sound.set_volume(VOL_SELECT)

    def update_position(self, scale_factor):
        super().update_position(scale_factor)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                self.button_sound.play()
                return True
            return False
        return False


class Slider():
    def __init__(self, x, y, width, height, fg, getvalue, setvalue, name, 
                 scale_factor, min_value=0, max_value=1):
        self.initial_x = x
        self.initial_y = y
        self.initial_width = width
        self.initial_height = height

        self.fg = fg
        self.scale_factor = scale_factor
        self.dragging = False

        self.min_value = min_value
        self.max_value = max_value

        self.get_value = getvalue
        self.set_value = setvalue
        actual = self.get_value()
        self.value = (actual - self.min_value) / (self.max_value - self.min_value)

        self.name = name

        self.fontsize = 16
        self.font = pygame.font.Font(resource_path(MAIN_FONT), self.fontsize)

        self.thumb_x = self.initial_x + int(self.value * self.initial_width)
        self.thumb_radius = self.initial_height * 1.2

        self.update_position(scale_factor)

    def update_position(self, scale_factor):
        self.scale_factor = scale_factor

        self.x = int(self.initial_x * scale_factor)
        self.y = int(self.initial_y * scale_factor)
        self.width = int(self.initial_width * scale_factor)
        self.height = int(self.initial_height * scale_factor)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.thumb_x = self.x + int(self.value * self.width)
        self.font = pygame.font.Font(None, int(self.fontsize * self.scale_factor))

        extra_click_height = int(self.height * 2.5)
        offset = (extra_click_height - self.height) // 2
        self.click_rect = pygame.Rect(
            self.x,
            self.y - offset,
            self.width,
            extra_click_height
        )

    def draw(self, surface):
        pygame.draw.rect(surface, self.fg, self.rect)
        pygame.draw.rect(surface, self.fg, self.rect, 2)

        thumb_center = (self.thumb_x, self.y + self.height // 2)
        pygame.draw.circle(surface, self.fg, thumb_center, self.thumb_radius)

        actual_value = self.min_value + self.value * (self.max_value - self.min_value)
        label = f"{self.name}: {round(actual_value, 2)}"
        text_surface = self.font.render(label, True, self.fg)

        surface.blit(text_surface, (self.x, self.y - self.fontsize - 5))

    def interact(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.click_rect.collidepoint(event.pos):
                self.dragging = True
                relative_x = max(self.x, min(event.pos[0], self.x + self.width))
                self.value = (relative_x - self.x) / self.width
                self.thumb_x = self.x + int(self.value * self.width)
        
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            self.update_value()
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.track_mouse(event.pos)

    def track_mouse(self, pos):
        relative_x = max(self.x, min(pos[0], self.x + self.width))
        self.value = (relative_x - self.x) / self.width
        self.thumb_x = self.x + int(self.value * self.width)

    def update_value(self):
        actual_value = self.min_value + self.value * (self.max_value - self.min_value)
        self.set_value(round(actual_value, 2))


class Timer:
    def __init__(self, game, x, y, width, height, fg, fontsize, max_time, scale_factor):
        self.game = game

        self.init_x = x
        self.init_y = y
        self.init_width = width
        self.init_height = height

        self.fg = fg # foreground color
        self.init_fontsize = fontsize

        self.font = pygame.font.Font(resource_path(MAIN_FONT), self.init_fontsize)

        self.max_time = max_time

        self.scale_factor = scale_factor

        self.update_position(self.scale_factor)

        self.start_time = pygame.time.get_ticks()

    def get_elapsed_time(self):
        curr_time = pygame.time.get_ticks()
        return (curr_time - self.start_time) // 1000
    
    def draw(self, surface, offset=(0,0)):
        elapsed = self.get_elapsed_time()
        time_left = self.max_time - elapsed
        text = self.font.render(("Timer: " + str(time_left)), True, self.fg)
        surface.blit(text, (self.x + offset[0], self.y + offset[1]))

    def reset_time(self):
        self.start_time = pygame.time.get_ticks()

    def times_up(self):
        elapsed = self.get_elapsed_time()
        time_left = self.max_time - elapsed
        if time_left == 0:
            return True
        return False

    def update_position(self, scale_factor):
        self.scale_factor = scale_factor

        self.x = int(self.init_x * self.scale_factor)
        self.y = int(self.init_y * self.scale_factor)
        self.width = int(self.init_width * self.scale_factor)
        self.height = int(self.init_height * self.scale_factor)

        self.fontsize = int(self.init_fontsize * self.scale_factor)
        self.font = pygame.font.Font(resource_path(MAIN_FONT), self.fontsize)


class Score(DisplayText):
    def __init__(self, x, y, width, height, fg, content, fontsize, scale_factor):
        super().__init__(x, y, width, height, fg, content, fontsize, scale_factor)
        self.score_val = 0

    def draw(self, surface, offset=(0,0)):
        text = self.font.render(("Score: " + str(self.score_val)), True, self.fg)
        surface.blit(text, (self.x + offset[0], self.y + offset[1]))

    def increase_score(self, points):
        self.score_val += points

    def reset_score(self):
        self.score_val = 0


class Lives(DisplayText):
    def __init__(self, game, x, y, width, height, fg, content, fontsize, scale_factor):
        super().__init__(x, y, width, height, fg, content, fontsize, scale_factor)
        self.game = game
        self.lives = 3

    def draw(self, surface, offset=(0,0)):
        text = self.font.render(("Lives: " + str(self.lives)), True, self.fg)
        surface.blit(text, (self.x + offset[0], self.y + offset[1]))

    def gain_life(self):
        self.lives += 1

    def lose_life(self):
        self.lives -= 1
        if self.lives == 0:
            self.game.lose()
        else:
            self.game.score.reset_score()
            self.game.reset_level()
        

    def reset_lives(self):
        self.lives = 3

