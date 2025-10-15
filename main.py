import pygame
from sprites import *
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

        self.font = pygame.font.Font(resource_path('assets/Cantarell.ttf'), 32)
        self.intro_background = pygame.image.load(resource_path("assets/img/DinioIntro.png"))
        self.go_background = pygame.image.load(resource_path("assets/img/GameOver.png"))
        self.gw_background = pygame.image.load(resource_path("assets/img/GameWin.png"))

        pygame.mixer.init()
        pygame.mixer.music.load(resource_path("assets/sounds/sky-loop.wav"))
        self.win_sound = pygame.mixer.Sound(resource_path("assets/sounds/level-win.wav"))
        self.win_sound.set_volume(.6)
        self.lose_sound = pygame.mixer.Sound(resource_path("assets/sounds/game-over.wav"))
        self.lose_sound.set_volume(.6)

        self.win = False

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                if column == "B":
                    Block(self, j, i)
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

        self.createTilemap()
        self.camera = Camera(WIN_WIDTH, WIN_HEIGHT, len(tilemap[0]) * TILESIZE, len(tilemap) * TILESIZE)
        
        pygame.mixer.music.play(-1)

    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.scale_factor = min(event.w / WIN_WIDTH, event.h / WIN_HEIGHT)

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.camera.update(self.player.sprites()[0])

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

            restart_button.update_position(button_x, button_y, button_width, button_height, self.scale_factor)

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

                    restart_button.update_position(button_x, button_y, button_width, button_height, self.scale_factor)

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

        while intro:
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
            
            play_button.update_position(button_x, button_y, button_width, button_height, self.scale_factor)

            adj_mouse_x = mouse_pos[0] - x_pad
            adj_mouse_y = mouse_pos[1] - y_pad
            adj_mouse_pos = (adj_mouse_x, adj_mouse_y)

            if play_button.is_pressed(adj_mouse_pos, mouse_pressed):
                intro = False

            scaled_intro_background = pygame.transform.scale(self.intro_background, (adj_width, adj_height))

            self.screen.fill(BLACK)
            self.screen.blit(scaled_intro_background, (x_pad, y_pad))
            self.screen.blit(play_button.image, (x_pad + button_x * self.scale_factor, y_pad + button_y * self.scale_factor))

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
