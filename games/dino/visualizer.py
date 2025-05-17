import pygame
import time
import games.dino.config as config
from games.dino.dino import Dino
from games.dino.obstacles import Obstacle
from games.dino.core_game import DinoCore
from core.agent import Agent
from core.ga import evolve_agents
from core.model_utils import save_best_agent



class DinoVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Training Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.generation = 1
        self.start_time = time.time()
        self.agents = []
        self.core = DinoCore()
        self.reset_generation()

    def reset_generation(self):
        if self.agents:
            fitness_scores = [self.scores[i] + getattr(self.dinos[i], 'time_alive', 0) for i in range(config.NUM_AGENTS)]
            best_index = max(range(config.NUM_AGENTS), key=lambda i: fitness_scores[i])
            save_best_agent(self.agents[best_index], fitness_scores[best_index], self.generation)
            self.agents = evolve_agents(self.agents, fitness_scores)
        else:
            self.agents = [Agent(config.INPUT_SIZE) for _ in range(config.NUM_AGENTS)]

        self.core.reset()
        self.dinos = [Dino(50, config.SCREEN_HEIGHT - config.GROUND_HEIGHT - config.DINO_HEIGHT) for _ in range(config.NUM_AGENTS)]
        self.scores = [0 for _ in range(config.NUM_AGENTS)]

    def get_inputs(self, dino, obstacle):
        dx = (obstacle.x - dino.x) / config.SCREEN_WIDTH if obstacle else 1.0
        height = obstacle.height / 50 if obstacle else 0.0
        y_pos = dino.y / config.SCREEN_HEIGHT
        y_vel = dino.velocity_y / 10.0
        return [dx, height, y_pos, y_vel]

    def find_next_obstacle(self, core):
        for obs in core.obstacles:
            if obs.x + obs.width > core.dino.x:
                return obs
        return None
    
    def update(self):
        self.core.update()  # Update shared obstacles

        next_obstacle = self.core.get_next_obstacle()
        alive_count = 0

        for i, dino in enumerate(self.dinos):
            if not dino.alive:
                continue

            inputs = self.get_inputs(dino, next_obstacle)
            if self.agents[i].decide(inputs):
                dino.jump()

            dino.update()
            dino.time_alive = getattr(dino, 'time_alive', 0) + 1

            if self.check_collision(dino):
                dino.alive = False
            else:
                alive_count += 1

            for obs in self.core.obstacles:
                if not obs.passed and obs.x + obs.width < dino.x:
                    obs.passed = True
                    self.scores[i] += 1

        if alive_count == 0:
            self.generation += 1
            self.reset_generation()

    def check_collision(self, dino):
        dino_bounds = dino.get_bounds()
        for obs in self.core.obstacles:
            o_bounds = obs.get_bounds()
            if (
                dino_bounds[2] > o_bounds[0] and dino_bounds[0] < o_bounds[2] and
                dino_bounds[3] > o_bounds[1] and dino_bounds[1] < o_bounds[3]
            ):
                return True
        return False

    def draw(self):
        self.screen.fill((255, 255, 255))
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (0, config.SCREEN_HEIGHT - config.GROUND_HEIGHT, config.SCREEN_WIDTH, config.GROUND_HEIGHT)
        )

        for obs in self.core.obstacles:
            obs.draw(self.screen)

        for dino in self.dinos:
            if dino.alive:
                dino.draw(self.screen)

        elapsed = time.time() - self.start_time
        current_best = max(self.scores)
        alive_count = sum(1 for d in self.dinos if d.alive)

        self.draw_text(f"Generation: {self.generation}", 10, 10)
        self.draw_text(f"Training Time: {elapsed:.1f}s", 10, 40)
        self.draw_text(f"Best Score (Gen): {current_best}", 10, 70)
        self.draw_text(f"Alive: {alive_count}/{config.NUM_AGENTS}", 10, 100)

        pygame.display.flip()

    def draw_text(self, text, x, y):
        label = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(label, (x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def run(self):
        running = True
        while running:
            self.clock.tick(config.FPS)
            running = self.handle_events()
            self.update()
            self.draw()

        pygame.quit()