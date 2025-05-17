"""
game.py

Contains the FlappyGame class, which implements the full Pygame-based
game. It supports manual control (via mouse), rendering, collision detection, 
and score tracking.
This script can be run standalone for testing or visualization.
"""

import pygame
from games.flappy import config
from games.flappy.core_game import GameCore


class FlappyGame:
    """
    A modular class to encapsulate game state and rendering using Pygame.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.background = pygame.image.load(config.BG_IMAGE).convert()
        self.background = pygame.transform.scale(self.background, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        self.bird_sprite = pygame.image.load(config.BIRD_SPRITE).convert_alpha()
        self.pipe_sprite_sheet = pygame.image.load(config.PIPE_SPRITE).convert_alpha()

        self.engine = GameCore(self.bird_sprite, self.pipe_sprite_sheet)
    
    
    # def run(self):
    #     running = True
    #     while running:
    #         self.clock.tick(config.FPS)
    #         running = self.handle_events()

    #         self.update()   # Uses agents to make decisions and update the game
    #         self.draw()

    #         # When all birds are dead, evolve to next generation
    #         if all(not bird.alive for bird in self.engine.birds):
    #             self.generation += 1
    #             self.reset_generation()

    #     pygame.quit()
        


    def run(self):
        running = True
        while running:
            self.clock.tick(config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.engine.alive:
                        self.engine.birds[0].jump()
                    else:
                        self.engine.reset()

            if self.engine.alive:
                self.engine.update()

            self.draw()

        pygame.quit()


    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for bird in self.engine.birds:
            bird.draw(self.screen)
        for pipe in self.engine.pipes:
            pipe.draw(self.screen)

        self.draw_text(f"Score: {self.engine.score}", 10, 10)
        if not self.engine.alive:
            self.draw_text("Game Over - Click to Restart", config.SCREEN_WIDTH // 2 - 120, config.SCREEN_HEIGHT // 2)

        pygame.display.flip()

    def draw_text(self, text, x, y):
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, (x, y))
