"""
bird.py

Defines the Bird class, representing the player or agent character in the game.
Handles movement mechanics such as gravity, jumping, and position tracking,
as well as bounding box calculations for collision detection.
"""

import pygame

class Bird:    
    """
    Class representing the player-controlled bird in the game.
    Manages position, velocity, gravity, and jump mechanics.
    """


    def __init__(self, x: float, y: float, sprite_sheet = None, radius: int = 10):
        """
        Initialize the bird with its position and default physics parameters.

        :param x: Initial horizontal position of the bird
        :param y: Initial vertical position of the bird
        :param radius: Radius of the bird (for collision detection)
        """
        self.x = x
        self.y = y
        self.radius = radius

        self.gravity = 0.5        # Acceleration due to gravity
        self.jump_strength = -8   # Velocity when jumping
        self.velocity_y = 0       # Vertical speed

        self.alive = True         # Status flag

        # Bird animation setup
        self.sprite_sheet = sprite_sheet
        self.frames = [
            pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i * 16, 0, 16, 16)), (24, 24))
            for i in range(4)
        ]
        self.frame_index = 0
        self.animation_counter = 0

        self.score = 0
        

    def update(self):
        """
        Apply gravity and update vertical position.
        """
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Animate
        self.animation_counter += 1
        if self.animation_counter % 5 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.frames)


    def jump(self):
        """
        Make the bird jump by setting upward velocity.
        """
        self.velocity_y = self.jump_strength


    def draw(self, surface):
        sprite = self.frames[self.frame_index]
        surface.blit(sprite, (int(self.x - self.radius), int(self.y - self.radius)))

    def get_position(self):
        """
        Get the current (x, y) position of the bird.

        :return: Tuple of (x, y)
        """
        return self.x, self.y
    
    def get_bounds(self):
        """
        Get the bounding box for collision detection.

        :return: Tuple (left, top, right, bottom)
        """
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )