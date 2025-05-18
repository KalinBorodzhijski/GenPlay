import pygame
import random
import games.dino.config as config

class Obstacle:
    """
    Represents a simple obstacle (cactus) in the Dino game.
    """

    def __init__(self, x, speed):
        self.image = pygame.image.load(config.CACTUS_SPRITE).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.x = x
        self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height
        self.speed = speed
        self.passed = False


    def update(self):
        self.x -= self.speed

    def is_off_screen(self):
        return self.x + self.width < 0

    def get_bounds(self):
        padding = 5
        return (
            self.x + padding,
            self.y + padding,
            self.x + self.width - padding,
            self.y + self.height - padding
        )

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class FlyingObstacle(Obstacle):
    def __init__(self, x, speed):
        super().__init__(x, speed)
        self.height = 40
        self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - 80