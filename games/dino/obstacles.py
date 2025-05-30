import pygame
import random
import games.dino.config as config

class BaseObstacle:
    def __init__(self, x, speed):
        self.x = x
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

class Obstacle(BaseObstacle):
    def __init__(self, x, speed):
        super().__init__(x, speed)
        self.image = pygame.image.load(config.CACTUS_SPRITE).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height

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


class FlyingObstacle(BaseObstacle):
    def __init__(self, x, speed):
        super().__init__(x, speed)

        self.sprite_sheet = pygame.image.load(config.BIRD_SPRITE).convert_alpha()
        frame_width, frame_height = 16, 15
        scale_factor = 2

        self.frames = []
        for i in range(8):
            frame = self.sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            scaled_frame = pygame.transform.scale(
                frame,
                (frame_width * scale_factor, frame_height * scale_factor)
            )
            self.frames.append(scaled_frame)

        self.image_index = 0
        self.image = self.frames[self.image_index]
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - 80
        self.animation_counter = 0

    def update(self):
        super().update()
        self.animation_counter += 1
        if self.animation_counter % 5 == 0:
            self.image_index = (self.image_index + 1) % len(self.frames)
            self.image = self.frames[self.image_index]