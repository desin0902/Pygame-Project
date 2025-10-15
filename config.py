import os
import sys

WIN_WIDTH = 640
WIN_HEIGHT = 480
TILESIZE = 20
FPS = 30
SCROLL = (0, 0)

PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32

PLAYER_LAYER = 3
BLOCK_LAYER = 1

PLAYER_SPEED = 4
PLAYER_JUMP_SPEED = 7
PLAYER_BOUNCE_SPEED = -10

ENEMY_HEIGHT = 18
ENEMY_WIDTH = 22

ENEMY_LAYER = 2

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
