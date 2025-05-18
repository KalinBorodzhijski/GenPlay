
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300
GROUND_HEIGHT = 40

GRAVITY = 0.6
JUMP_VELOCITY = -9

FPS = 60

DINO_WIDTH = 40
DINO_HEIGHT = 40

MIN_OBSTACLE_DELAY = 600    # ms
MAX_OBSTACLE_DELAY = 1500   # ms

DINO_DUCK_FRAMES = list(range(19, 24))

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

DINO_SPRITESHEET = os.path.join(ASSETS_PATH, "dino_spritesheet.png")
CACTUS_SPRITE = os.path.join(ASSETS_PATH, "cactus.png")
BACKGROUND_IMAGE = os.path.join(ASSETS_PATH, "background.jpg")

# Training parameters
NUM_AGENTS = 1000
INPUT_SIZE = 5
