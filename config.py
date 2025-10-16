import os
import sys

WIN_WIDTH = 640
WIN_HEIGHT = 480
TILESIZE = 20
FPS = 30
SCROLL = (0, 0)

ASSETS_DIR = "assets"

IMG_DIR = f"{ASSETS_DIR}/img"
SPRITES_DIR = IMG_DIR
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
FONT_DIR = ASSETS_DIR

IMG_INTRO = f"{IMG_DIR}/DinioIntro.png"
IMG_GAME_OVER = f"{IMG_DIR}/GameOver.png"
IMG_GAME_WIN = f"{IMG_DIR}/GameWin.png"

SPRITE_FLAG = f"{SPRITES_DIR}/GameWinFlag.png"
SPRITE_BRICK_1 = f"{SPRITES_DIR}/Brick 1.png"
SPRITE_BRICK_2 = f"{SPRITES_DIR}/Brick 2.png"

MUSIC_MAIN = f"{SOUNDS_DIR}/sky-loop.wav"
SOUND_WIN = f"{SOUNDS_DIR}/level-win.wav"
SOUND_GAME_OVER = f"{SOUNDS_DIR}/game-over.wav"
SOUND_MENU_SELECT = f"{SOUNDS_DIR}/menu-select.mp3"

SOUND_JUMP = f"{SOUNDS_DIR}/jumping.wav"
SOUND_BOUNCE = f"{SOUNDS_DIR}/enemy-bounce.mp3"

VOL_SELECT = 0.4
VOL_SOUND = 0.6
VOL_JUMP = 0.2
VOL_BOUNCE = 0.3

MAIN_FONT = f"{FONT_DIR}/Cantarell.ttf"
FONT_SIZE = 32

TILEMAP_1 = f"{ASSETS_DIR}/tilemap.txt"

PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32

PLAYER_LAYER = 3
BLOCK_LAYER = 1

PLAYER_SPEED = 4
PLAYER_JUMP_SPEED = 7
PLAYER_BOUNCE_SPEED = -10

# Animation States
PLAYER_IDLE = 0
PLAYER_BLINK = 1
PLAYER_RUN = 2
PLAYER_JUMP = 3
PLAYER_WAG = 4

PLAYER_ANIMATION_SPEED = 250

ENEMY_WALK = 0
ENEMY_SMUSH = 1

ENEMY_ANIMATION_SPEED = 250
ENEMY_DIE_SPEED = 75

ENEMY_HEIGHT = 18
ENEMY_WIDTH = 22

ENEMY_LAYER = 2

SPRITE_PLAYER = f"{SPRITES_DIR}/single.png"
SPRITE_ENEMY_1 = f"{SPRITES_DIR}/Mob1.png"

GRAVITY = .4
FRICTION = .25

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

def resource_path(relative_path):
    """ Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_tilemap(file_path):
    with open(file_path, 'r') as file:
        tilemap = [line.strip() for line in file.readlines()]
    return tilemap

tilemap = load_tilemap(resource_path('assets/tilemap.txt'))
