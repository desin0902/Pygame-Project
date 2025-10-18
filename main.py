import pygame
from sprites import *
from utils import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)

        pygame.display.set_caption('Dinio')
        self.clock = pygame.time.Clock()
        self.running = True
        self.scale_factor = 1

        self.font = pygame.font.Font(resource_path(MAIN_FONT), FONT_SIZE)
        self.intro_background = pygame.image.load(resource_path(IMG_INTRO))
        self.go_background = pygame.image.load(resource_path(IMG_GAME_OVER))
        self.gw_background = pygame.image.load(resource_path(IMG_GAME_WIN))

        self.levels = LEVELS
        self.level_index = 0

        self.timer = Timer(game=self, x=WIN_WIDTH-105, y=0, 
                           width=100, height=50, fg=(100, 100, 100), 
                           fontsize=20, max_time=99, 
                           scale_factor=self.scale_factor)
        
        score_width = 120
        score_x = (WIN_WIDTH - score_width) / 2
        self.score = Score(x=score_x, y=0, width=score_width,
                           height=50, fg=(100, 100, 100),
                           content='0', fontsize=20, 
                           scale_factor=self.scale_factor)
        
        self.lives = Lives(game=self, x=10, y=0, width=100, height=50, fg=(100, 100, 100),
                           content = '3', fontsize=20, 
                           scale_factor=self.scale_factor)

        pygame.mixer.init()
        pygame.mixer.music.load(resource_path(MUSIC_MAIN))
        self.win_sound = pygame.mixer.Sound(resource_path(SOUND_WIN))
        self.win_sound.set_volume(VOL_SOUND)
        self.lose_sound = pygame.mixer.Sound(resource_path(SOUND_GAME_OVER))
        self.lose_sound.set_volume(VOL_SOUND)

        self.win = False

    def createTilemap(self, level):
        for i, row in enumerate(level):
            for j, column in enumerate(row):
                if column == "B":
                    Block1(self, j, i)
                if column == "G":
                    Block2(self, j, i)
                if column == "P":
                    Player(self, j, i)
                if column == "E":
                    Enemy(self, j, i)
                if column == "F":
                    Flag(self, j, i)

    def new(self):
        #a new game starts
        self.playing = True
        self.win = False
        self.waiting_for_restart = False

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.player = pygame.sprite.LayeredUpdates()
        self.enemy = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.flag = pygame.sprite.LayeredUpdates()

        self.level_index = 0

        self.createTilemap(self.levels[self.level_index])
        self.camera = Camera(WIN_WIDTH, WIN_HEIGHT, 
                             len(self.levels[self.level_index][0]) * TILESIZE, 
                             len(self.levels[self.level_index]) * TILESIZE)
        
        self.timer.reset_time()
        self.timer.update_position(self.scale_factor)

        self.score.reset_score()
        self.score.update_position(self.scale_factor)

        self.lives.reset_lives()
        self.lives.update_position(self.scale_factor)
        
        pygame.mixer.music.play(-1)

    def reset_level(self):
        for sprite in self.all_sprites:
            sprite.kill()

        self.timer.reset_time()
        self.timer.update_position(self.scale_factor)

        self.score.update_position(self.scale_factor)

        self.lives.update_position(self.scale_factor)

        self.camera = Camera(WIN_WIDTH, WIN_HEIGHT, 
                             len(self.levels[self.level_index][0]) * TILESIZE, 
                             len(self.levels[self.level_index]) * TILESIZE)

        self.createTilemap(self.levels[self.level_index])

        pygame.mixer.music.play(-1)

    def next_level(self):
        self.level_index += 1
        if self.level_index < len(LEVELS):
            self.reset_level()
        else:
            self.win_game()

    def lose(self):
        self.win = False
        self.playing = False

    def win_game(self):
        self.win = True
        self.playing = False

    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.scale_factor = min(event.w / WIN_WIDTH, event.h / WIN_HEIGHT)
                self.timer.update_position(self.scale_factor)
                self.score.update_position(self.scale_factor)
                self.lives.update_position(self.scale_factor)

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.camera.update(self.player.sprites()[0])

        if self.timer.times_up():
            self.lives.lose_life()

    def draw(self):
        #game loop draw
        predraw_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        predraw_surface.fill(LIGHT_BLUE)
        for sprite in self.all_sprites:
            predraw_surface.blit(sprite.image, self.camera.apply(sprite))

        adj_width = int(WIN_WIDTH * self.scale_factor)
        adj_height = int(WIN_HEIGHT * self.scale_factor)

        scaled_surface = pygame.transform.scale(predraw_surface, (adj_width, adj_height))

        x_pad = (self.screen.get_width() - adj_width) // 2
        y_pad = (self.screen.get_height() - adj_height) // 2

        self.screen.fill((BLACK))
        self.screen.blit(scaled_surface, (x_pad, y_pad))

        self.timer.draw(self.screen, offset=(x_pad, y_pad))
        self.score.draw(self.screen, offset=(x_pad, y_pad))
        self.lives.draw(self.screen, offset=(x_pad, y_pad))

        self.clock.tick(FPS)
        pygame.display.update()

    def main(self):
        #game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        pygame.mixer.music.stop()
        self.lose_sound.play()

        self.waiting_for_restart = True

        button_width = 120
        button_height = 50
        button_x = (WIN_WIDTH - button_width) / 2
        button_y = (WIN_HEIGHT - button_height) / 2
        restart_button = Button(button_x, button_y, button_width, button_height, WHITE, BLACK, 'Restart', 32, self.scale_factor)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.waiting_for_restart and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            screen_width, screen_height = self.screen.get_size()
            self.scale_factor = min(screen_width / WIN_WIDTH, screen_height / WIN_HEIGHT)
            adj_width = int(WIN_WIDTH * self.scale_factor)
            adj_height = int(WIN_HEIGHT * self.scale_factor)
            x_pad = (screen_width - adj_width) // 2
            y_pad = (screen_height - adj_height) // 2

            restart_button.update_position(self.scale_factor)

            adj_mouse_x = mouse_pos[0] - x_pad
            adj_mouse_y = mouse_pos[1] - y_pad
            adj_mouse_pos = (adj_mouse_x, adj_mouse_y)

            if restart_button.is_pressed(adj_mouse_pos, mouse_pressed):
                self.waiting_for_restart = False
                return

            scaled_go_background = pygame.transform.scale(self.go_background, (adj_width, adj_height))

            self.screen.fill(BLACK)
            self.screen.blit(scaled_go_background, (x_pad, y_pad))
            self.screen.blit(restart_button.image, (x_pad + button_x * self.scale_factor, y_pad + button_y * self.scale_factor))
            self.clock.tick(FPS)
            pygame.display.update()

    def game_win(self):
        for sprite in self.player:
            if isinstance(sprite, Player):
                pygame.mixer.music.stop()
                self.win_sound.play()

                self.waiting_for_restart = True

                button_width = 120
                button_height = 50
                button_x = (WIN_WIDTH - button_width) / 2
                button_y = (WIN_HEIGHT - button_height) / 2
                restart_button = Button(button_x, button_y, button_width, button_height, WHITE, BLACK, 'Restart', 32, self.scale_factor)

                for sprite in self.all_sprites:
                    sprite.kill()

                while self.waiting_for_restart and self.running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False

                    mouse_pos = pygame.mouse.get_pos()
                    mouse_pressed = pygame.mouse.get_pressed()

                    screen_width, screen_height = self.screen.get_size()
                    self.scale_factor = min(screen_width / WIN_WIDTH, screen_height / WIN_HEIGHT)
                    adj_width = int(WIN_WIDTH * self.scale_factor)
                    adj_height = int(WIN_HEIGHT * self.scale_factor)
                    x_pad = (screen_width - adj_width) // 2
                    y_pad = (screen_height - adj_height) // 2

                    restart_button.update_position(self.scale_factor)

                    adj_mouse_x = mouse_pos[0] - x_pad
                    adj_mouse_y = mouse_pos[1] - y_pad
                    adj_mouse_pos = (adj_mouse_x, adj_mouse_y)

                    if restart_button.is_pressed(adj_mouse_pos, mouse_pressed):
                        self.waiting_for_restart = False
                        return

                    scaled_gw_background = pygame.transform.scale(self.gw_background, (adj_width, adj_height))

                    self.screen.fill(BLACK)
                    self.screen.blit(scaled_gw_background, (x_pad, y_pad))
                    self.screen.blit(restart_button.image, (x_pad + button_x * self.scale_factor, y_pad + button_y * self.scale_factor))
                    self.clock.tick(FPS)
                    pygame.display.update()
            else:
                pass

    def intro_screen(self):
        intro = True

        button_width = 100
        button_height = 50
        button_x = (WIN_WIDTH - button_width) / 2
        button_y = (WIN_HEIGHT - button_height - 100) / 2
        play_button = Button(button_x, button_y, button_width, button_height, WHITE, BLACK, 'Play', 32, self.scale_factor)
        options_button = Button(x=WIN_WIDTH-140, y=0, width=120, height=50, 
                                fg=WHITE, bg=BLACK, content='Options', 
                                fontsize=32, scale_factor=self.scale_factor)

        while intro and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            screen_width, screen_height = self.screen.get_size()
            self.scale_factor = min(screen_width / WIN_WIDTH, screen_height / WIN_HEIGHT)
            adj_width = int(WIN_WIDTH * self.scale_factor)
            adj_height = int(WIN_HEIGHT * self.scale_factor)
            x_pad = (screen_width - adj_width) // 2
            y_pad = (screen_height - adj_height) // 2
            
            play_button.update_position(self.scale_factor)
            options_button.update_position(self.scale_factor)

            adj_mouse_x = mouse_pos[0] - x_pad
            adj_mouse_y = mouse_pos[1] - y_pad
            adj_mouse_pos = (adj_mouse_x, adj_mouse_y)

            scaled_intro_background = pygame.transform.scale(self.intro_background, (adj_width, adj_height))

            self.screen.fill(BLACK)
            self.screen.blit(scaled_intro_background, (x_pad, y_pad))
            self.screen.blit(play_button.image, (x_pad + button_x * self.scale_factor, y_pad + button_y * self.scale_factor))
            self.screen.blit(options_button.image, (x_pad + options_button.initial_x * self.scale_factor, y_pad + options_button.initial_y * self.scale_factor))

            self.clock.tick(FPS)
            pygame.display.update()

            if play_button.is_pressed(adj_mouse_pos, mouse_pressed):
                intro = False

            if options_button.is_pressed(adj_mouse_pos, mouse_pressed):
                self.options_screen()

    def options_screen(self):
        options = True

        exit_button = Button(x=10, y=0, width=100, height=50, 
                                fg=WHITE, bg=BLACK, content='Exit', 
                                fontsize=32, scale_factor=self.scale_factor)
        
        gravity_slider = Slider(x=150, y=200, width=280, height=10, 
                                fg=WHITE, getvalue=lambda: config.GRAVITY, 
                                setvalue=lambda val: setattr(config, "GRAVITY", val),
                                name="Gravity", scale_factor=self.scale_factor)
        
        friction_slider = Slider(x=150, y=250, width=280, height=10, 
                                fg=WHITE, getvalue=lambda: config.FRICTION, 
                                setvalue=lambda val: setattr(config, "FRICTION", val),
                                name="Friction", scale_factor=self.scale_factor)
        
        air_res_slider = Slider(x=150, y=300, width=280, height=10, 
                                fg=WHITE, getvalue=lambda: config.AIR_RESISTANCE, 
                                setvalue=lambda val: setattr(config, "AIR_RESISTANCE", val),
                                name="Air Resistance", scale_factor=self.scale_factor)
        
        player_speed_slider = Slider(x=150, y=350, width=280, height=10, 
                                fg=WHITE, getvalue=lambda: config.PLAYER_SPEED, 
                                setvalue=lambda val: setattr(config, "PLAYER_SPEED", val),
                                name="Acceleration", scale_factor=self.scale_factor,
                                max_value=5)
        
        max_speed_slider = Slider(x=150, y=400, width=280, height=10, 
                                fg=WHITE, getvalue=lambda: config.PLAYER_MAX_SPEED, 
                                setvalue=lambda val: setattr(config, "PLAYER_MAX_SPEED", val),
                                name="Max Speed", scale_factor=self.scale_factor, 
                                max_value=100)

        while options and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options = False
                    self.running = False

                gravity_slider.interact(event)
                friction_slider.interact(event)
                air_res_slider.interact(event)
                player_speed_slider.interact(event)
                max_speed_slider.interact(event)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            screen_width, screen_height = self.screen.get_size()
            self.scale_factor = min(screen_width / WIN_WIDTH, screen_height / WIN_HEIGHT)
            adj_width = int(WIN_WIDTH * self.scale_factor)
            adj_height = int(WIN_HEIGHT * self.scale_factor)
            x_pad = (screen_width - adj_width) // 2
            y_pad = (screen_height - adj_height) // 2
            
            exit_button.update_position(self.scale_factor)
            gravity_slider.update_position(self.scale_factor)
            friction_slider.update_position(self.scale_factor)
            air_res_slider.update_position(self.scale_factor)
            player_speed_slider.update_position(self.scale_factor)
            max_speed_slider.update_position(self.scale_factor)

            adj_mouse_x = mouse_pos[0] - x_pad
            adj_mouse_y = mouse_pos[1] - y_pad
            adj_mouse_pos = (adj_mouse_x, adj_mouse_y)

            if exit_button.is_pressed(adj_mouse_pos, mouse_pressed):
                options = False

            scaled_intro_background = pygame.transform.scale(self.intro_background, (adj_width, adj_height))

            self.screen.fill(BLACK)
            self.screen.blit(scaled_intro_background, (x_pad, y_pad))
            self.screen.blit(exit_button.image, (x_pad + 10 * self.scale_factor, y_pad + 0 * self.scale_factor))
            gravity_slider.draw(self.screen)
            friction_slider.draw(self.screen)
            air_res_slider.draw(self.screen)
            player_speed_slider.draw(self.screen)
            max_speed_slider.draw(self.screen)

            self.clock.tick(FPS)
            pygame.display.update()

g = Game()
g.intro_screen()
while g.running:
    g.new()
    g.main()

    if g.win:
        g.game_win()
    else:
        g.game_over()

pygame.quit()
sys.exit()
