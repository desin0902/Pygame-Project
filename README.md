# Pygame-Project
A game engine and game built in pygame, aimed at praticing classes, objects, and splitting a project across multiple files for added modularity and simplified expansion.

Contents:
img: An images folder containing all the sprites in the game, as well as backgrounds and transition screens.

sounds: A folder containing all of the sound effects and music for the game. All if it creative commons from freesound.org.

Cantarell.ttf: The font used for the games restart button.

config.py: Contains values used repeatedly throughout the game to simplify variables, as well as a tilemap unpacker for simplified expansion of the game's maps.

main.py: The main game file, containing the game's main loop and its different screens.

sprites.py: Contains the different sprite classes in the game, the camera, collision detection, the button function, sound effects, and sprite animation management.

spritesheet.py: Contains a function that simplifies use of spritesheets for animation in sprites.py.

tilemap.txt: The first map of the game, separated into a .txt file for easy management and expansion.
