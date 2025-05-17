"""
pipe.py

Defines the Pipe class, which represents an obstacle in the game.
Each pipe consists of a top and bottom section with a vertical gap.
This class handles movement, random gap positioning, and collision bounds.
"""

import random, pygame
from games.flappy import config

class Pipe:
    """
    Class representing a pair of pipes (top and bottom) as an obstacle.
    """

    
    def __init__(self, x: float, image, gap_size: int = config.PIPE_GAP_SIZE, width: int = config.PIPE_WIDTH):
        """
        Initialize a new pipe with a random gap position.

        :param x: Initial horizontal position of the pipe
        :param gap_size: Vertical space between top and bottom pipes
        :param width: Width of the pipe
        """
        self.x = x
        self.width = width
        self.gap_size = gap_size
        
        self.passed = False
        self.speed = config.PIPE_SPEED

        # Random vertical position of the gap (top of the gap)
        self.gap_y = random.randint(100, config.SCREEN_HEIGHT - 200)

    
        self.image = image
        self.image_width = image.get_width()
        self.image_height = image.get_height()

    def draw(self, surface):
        """
        Draw vertically stretched top and bottom pipes.
        """
        # Top pipe
        top_height = self.gap_y
        top_scaled = pygame.transform.scale(self.image, (self.width, int(top_height)))
        surface.blit(top_scaled, (int(self.x), 0))

        # Bottom pipe
        bottom_y = self.gap_y + self.gap_size
        bottom_height = config.SCREEN_HEIGHT - bottom_y
        bottom_scaled = pygame.transform.scale(self.image, (self.width, int(bottom_height)))
        surface.blit(bottom_scaled, (int(self.x), int(bottom_y)))

    def update(self):
        """
        Move the pipe leftward.
        """
        self.x -= self.speed

    
    def is_off_screen(self):
        """
        Check if the pipe has moved off the screen.

        :return: True if off screen
        """
        return self.x + self.width < 0
    
    
    def get_bounds(self):
        """
        Get the bounding boxes for top and bottom pipes.

        :return: Tuple of two bounding boxes (top_rect, bottom_rect), each as (left, top, right, bottom)
        """
        top_rect = (self.x, 0, self.x + self.width, self.gap_y)
        bottom = (self.x, self.gap_y + self.gap_size, self.x + self.width, config.SCREEN_HEIGHT)
        return top_rect, bottom
