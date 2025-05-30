import pygame
from games.dino.visualizer import DinoVisualizerWithConfig
from core.experiments.experiment_config import ExperimentConfig
from games.flappy.visualizer import FlappyVisualizerWithConfig

from games.flappy import config as flappy_config
from games.dino import config as dino_config

class MultiExperimentVisualizer:
    def __init__(self, experiment_configs):
        self.configs = experiment_configs
        self.screen_width, self.screen_height = self.layout_experiments(self.configs)

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Multi-Experiment Visualizer")
        self.clock = pygame.time.Clock()

        self.experiments = []
        for cfg in self.configs:
            if cfg.game_type == "dino":
                self.experiments.append(DinoVisualizerWithConfig(cfg, self.screen))
            elif cfg.game_type == "flappy":
                self.experiments.append(FlappyVisualizerWithConfig(cfg, self.screen))
            else:
                raise ValueError("Unknown game type")

    def run(self):
        running = True
        while running:
            self.clock.tick(flappy_config.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((255, 255, 255))
            for exp in self.experiments:
                exp.update()
                exp.draw()
            pygame.display.flip()
        pygame.quit()

    def layout_experiments(self, configs: list[ExperimentConfig]):
        dino_height = dino_config.SCREEN_HEIGHT
        dino_width = dino_config.SCREEN_WIDTH
        flappy_height = flappy_config.SCREEN_HEIGHT
        flappy_width = flappy_config.SCREEN_WIDTH

        dino_configs = [cfg for cfg in configs if cfg.game_type == "dino"]
        flappy_configs = [cfg for cfg in configs if cfg.game_type == "flappy"]

        for i, cfg in enumerate(dino_configs):
            cfg.position = (0, i * dino_height)

        for i, cfg in enumerate(flappy_configs):
            cfg.position = (i * flappy_width, 0)

        screen_width = max(
            dino_width,
            flappy_width * len(flappy_configs)
        )
        screen_height = max(
            flappy_height,
            dino_height * len(dino_configs)
        )

        return screen_width, screen_height