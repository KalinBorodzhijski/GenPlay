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
        self.dino = Dino(50, config.SCREEN_HEIGHT - config.GROUND_HEIGHT - config.DINO_HEIGHT)
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
        # Obstacles and dino
        for obs in self.core.obstacles:
            obs.draw(self.screen)

        self.dino.draw(self.screen)

        # Score
        self.draw_text(f"Score: {getattr(self.dino, 'score', 0)}", 10, 10)

        if not self.dino.alive:
                self.draw_text("Game Over - Click to Restart", config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT // 2)


        pygame.display.flip()

    def draw_text(self, text, x, y):
        label = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(label, (x, y))

    def handle_events(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.dino.alive:
                    if not self.dino.is_ducking:
                        self.dino.jump()
                else:
                    self.reset()

        # Ducking
        if self.dino.on_ground and self.dino.alive:
            if keys[pygame.K_SPACE]:
                self.dino.duck()
            else:
                self.dino.stand_up()

    def reset(self):
        self.core.reset()
        self.dino = Dino(50, config.SCREEN_HEIGHT - config.GROUND_HEIGHT - config.DINO_HEIGHT)


    def run(self):
        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            if self.dino.alive:
                self.core.update([self.dino])
            self.draw()

        pygame.quit()