import pygame
import random
from games.dino.dino import Dino
from games.dino.obstacles import Obstacle
import games.dino.config as config
from games.dino.core_game import DinoCore

class DinoGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.core = DinoCore()
        self.running = True

    def draw(self):
        # Fill background with solid color
        self.screen.fill((240, 240, 240))  # light gray

        # Draw ground
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),  # dark gray ground
            (0, config.SCREEN_HEIGHT - config.GROUND_HEIGHT, config.SCREEN_WIDTH, config.GROUND_HEIGHT)
        )
        # Draw dino and obstacles
        self.core.dino.draw(self.screen)
        for obs in self.core.obstacles:
            obs.draw(self.screen)

        # Score
        self.screen.blit(self.font.render(f"Score: {self.core.score}", True, (0, 0, 0)), (10, 10))

        if not self.core.dino.alive:
            self.screen.blit(
                self.font.render("Game Over - Click to Restart", True, (0, 0, 0)),
                (config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT // 2)
            )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.core.dino.alive:
                    self.core.dino.jump()
                else:
                    self.core.reset()

    def run(self):
        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            if self.core.dino.alive:
                self.core.update()
            self.draw()

        pygame.quit()