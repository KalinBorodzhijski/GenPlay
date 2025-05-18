SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
PIPE_SPACING = 200
PIPE_INTERVAL = 1500  # ms between new pipes
FPS = 60

# Vertical space between top and bottom pipes
PIPE_GAP_SIZE = 100
# Width of the pipe
PIPE_WIDTH = 32
# Pipe movement speed to the left
PIPE_SPEED = 3

BACKGROUND_COLOR = (30, 30, 30)
BIRD_COLOR = (255, 200, 0)
PIPE_COLOR = (100, 255, 100)
# Asset paths
ASSET_PATH = "games/flappy/assets"
BG_IMAGE = f"{ASSET_PATH}/Background.png"
BIRD_SPRITE = f"{ASSET_PATH}/Bird.png"


PIPE_SPRITE = f"{ASSET_PATH}/PipeStyle.png"
IMAGE_PIPE_WIDTH = 32
IMAGE_PIPE_HEIGHT = 80

#Training parameters
NUM_AGENTS = 2000
SAVE_MODEL_PATH = "model/flappy_best.pkl"