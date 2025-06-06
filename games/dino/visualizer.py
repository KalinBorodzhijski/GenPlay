import pygame
import time
import games.dino.config as dino_config
from games.dino.dino import Dino
from games.dino.obstacles import FlyingObstacle
from games.dino.core_game import DinoCore
from core.agent import Agent
from core.ga import evolve_agents
from core.model_utils import *

from core.network_visualization import draw_network_visualization
from core.experiments.experiment_config import ExperimentConfig
class DinoVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((dino_config.SCREEN_WIDTH, dino_config.SCREEN_HEIGHT))
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
            fitness_scores = [self.scores[i] for i in range(dino_config.NUM_AGENTS)]
            best_index = max(range(dino_config.NUM_AGENTS), key=lambda i: fitness_scores[i])
            save_best_agent(self.agents[best_index], fitness_scores[best_index], self.generation, dino_config.SAVE_MODEL_PATH)
            self.agents = evolve_agents(self.agents, fitness_scores)
        else:
            self.agents = [Agent(dino_config.INPUT_SIZE) for _ in range(dino_config.NUM_AGENTS)]

        self.core.reset()
        self.dinos = [Dino(50, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT - dino_config.DINO_HEIGHT) for _ in range(dino_config.NUM_AGENTS)]
        self.scores = [0 for _ in range(dino_config.NUM_AGENTS)]

    def get_inputs(self, dino, obstacle):
        if obstacle:
            dx = (obstacle.x - dino.x) / dino_config.SCREEN_WIDTH
            dy = (obstacle.y - dino.y) / dino_config.SCREEN_HEIGHT
            obstacle_height = obstacle.height / dino_config.SCREEN_HEIGHT
            obstacle_width = obstacle.width / dino_config.SCREEN_WIDTH
            obstacle_speed = obstacle.speed / dino_config.BASE_SPEED
            time_to_collision = dx / (obstacle.speed + 1e-5)
            is_flying = 1.0 if isinstance(obstacle, FlyingObstacle) else 0.0
            is_ground = 1.0 - is_flying
        else:
            dx = 1.0
            dy = 0.0
            obstacle_height = 0.0
            obstacle_width = 0.0
            obstacle_speed = 0.0
            time_to_collision = 1.0
            is_flying = 0.0
            is_ground = 0.0

        return [
            dino.y / dino_config.SCREEN_HEIGHT,
            dino.velocity_y / 10.0,
            dx,
            dy,
            obstacle_height,
            obstacle_width,
            obstacle_speed,
            time_to_collision,
            is_flying,
            is_ground,
            0.0, 1.0  # one-hot: Flappy, Dino
        ]

    def find_next_obstacle(self, core):
        for obs in core.obstacles:
            if obs.x + obs.width > core.dino.x:
                return obs
        return None
    
    def update(self):
        self.core.update(self.dinos)  # Update shared obstacles

        next_obstacle = self.core.get_next_obstacle()
        alive_count = 0
        best_score = 0
        best_index = -1

        for i, dino in enumerate(self.dinos):
            if not dino.alive:
                continue

            inputs = self.get_inputs(dino, next_obstacle)
            _, dino_jump, duck = self.agents[i].decide(inputs)
            # Prioritize jump over duck
            if dino_jump:
                dino.jump()
                dino.stand_up()
            elif duck:
                dino.duck()
            else:
                dino.stand_up()

            if self.check_collision(dino):
                dino.alive = False
            else:
                alive_count += 1

            for obs in self.core.obstacles:
                if not obs.passed and obs.x + obs.width < dino.x:
                    obs.passed = True
                    self.scores[i] = getattr(dino, 'score', 0)

                    if self.scores[i] > best_score:
                        best_score = self.scores[i]
                        best_index = i

        if best_score % 50 == 0 and best_score != 0:
            if best_index != -1:
                save_best_agent(self.agents[best_index], best_score, self.generation, dino_config.SAVE_MODEL_PATH)
                print(f"[Checkpoint] Saved agent at score {best_score}")

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
            (0, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT, dino_config.SCREEN_WIDTH, dino_config.GROUND_HEIGHT)
        )

        for obs in self.core.obstacles:
            obs.draw(self.screen)

        for dino in self.dinos:
            if dino.alive:
                dino.draw(self.screen)

        elapsed = time.time() - self.start_time
        current_score = max(self.scores[i] for i in range(dino_config.NUM_AGENTS) if self.dinos[i].alive) if any(d.alive for d in self.dinos) else 0
        alive_count = sum(1 for d in self.dinos if d.alive)

        self.draw_text(f"Generation: {self.generation}", 10, 10)
        self.draw_text(f"Training Time: {elapsed:.1f}s", 10, 40)
        self.draw_text(f"Score: {current_score}", 10, 70)
        self.draw_text(f"Alive: {alive_count}/{dino_config.NUM_AGENTS}", 10, 100)

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
            self.clock.tick(dino_config.FPS)
            running = self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
    
    def watch_best(self, model_path=None):
        """
        Loads and plays the best saved agent on the Dino game.
        :param model_path: Path to the saved model. If None, uses the default path.
        """
        visualizer_enabled = False

        path = model_path if model_path else dino_config.SAVE_MODEL_PATH
        best = load_best_agent(path)
        if not best:
            print("No saved Dino agent found.")
            return

        agent = create_agent_from_genome(best["genome"], input_size=dino_config.INPUT_SIZE)
        dino = Dino(50, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT - dino_config.DINO_HEIGHT)
        core = DinoCore()

        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(dino_config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        visualizer_enabled = not visualizer_enabled

            core.update([dino])  # update game world with the single dino

            # Get next obstacle
            next_obstacle = core.get_next_obstacle()

            # Build input vector
            inputs = self.get_inputs(dino, next_obstacle)

            _, dino_jump, duck, activations = agent.decide_with_activations(inputs)
            if dino_jump:
                dino.jump()
                dino.stand_up()
            elif duck:
                dino.duck()
            else:
                dino.stand_up()

            self.screen.fill((255, 255, 255))
            pygame.draw.rect(
                self.screen,
                (100, 100, 100),
                (0, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT, dino_config.SCREEN_WIDTH, dino_config.GROUND_HEIGHT)
            )

            for obs in core.obstacles:
                obs.draw(self.screen)

            if dino.alive:
                dino.draw(self.screen)

            self.draw_text(f"Best Agent - Gen {best['generation']} / Fitness: {best['fitness']:.2f}", 10, 10)
            self.draw_text(f"Score: {getattr(dino, 'score', 0)}", 10, 40)
            input_labels = [
                "Dino Y",              # 1
                "Vertical Velocity",   # 2
                "Distance to Obstacle",# 3
                "Vertical Distance to Obstacle",  # 4
                "Obstacle Height",     # 5
                "Obstacle Width",      # 6
                "Obstacle Speed",      # 7
                "Time to Collision",   # 8
                "Is Flying Obstacle",  # 9
                "Is Ground Obstacle",  #10
                "Flappy Game",         #11
                "Dino Game"            #12
            ]

            output_labels = ["Dino Jump", "Duck"]
            if visualizer_enabled:
                draw_network_visualization(self.screen, activations,input_labels=input_labels, output_labels=output_labels)

            pygame.display.flip()

            if not dino.alive:
                pygame.time.wait(1500)
                running = False

        pygame.quit()


class DinoVisualizerWithConfig(DinoVisualizer):
    def __init__(self, experiment_config: ExperimentConfig, shared_screen):
        self.experiment_config = experiment_config
        self.screen = shared_screen
        self.position = experiment_config.position
        self.mutation_rate = experiment_config.mutation_rate
        self.retain_top = experiment_config.retain_top
        dino_config.NUM_AGENTS = experiment_config.num_agents

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.generation = 1
        self.start_time = time.time()
        self.agents = []
        self.core = DinoCore()

        self.reset_generation()

    def reset_generation(self):
        if self.agents:
            fitness_scores = [self.scores[i] for i in range(len(self.agents))]
            self.agents = evolve_agents(
                self.agents,
                fitness_scores,
                retain_top=self.retain_top,
                mutate_rate=self.mutation_rate
            )
        else:
            self.agents = [
                Agent(dino_config.INPUT_SIZE)
                for _ in range(self.experiment_config.num_agents)
            ]

        self.core.reset()
        self.dinos = [
            Dino(
                50,
                dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT - dino_config.DINO_HEIGHT
            ) for _ in range(self.experiment_config.num_agents)
        ]
        self.scores = [0 for _ in range(self.experiment_config.num_agents)]

    def draw(self):
        surface = pygame.Surface((dino_config.SCREEN_WIDTH, dino_config.SCREEN_HEIGHT))
        surface.fill((255, 255, 255))

        pygame.draw.rect(
            surface,
            (100, 100, 100),
            (0, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT,
             dino_config.SCREEN_WIDTH, dino_config.GROUND_HEIGHT)
        )

        for obs in self.core.obstacles:
            obs.draw(surface)

        for dino in self.dinos:
            if dino.alive:
                dino.draw(surface)

        elapsed = time.time() - self.start_time
        alive_count = sum(1 for d in self.dinos if d.alive)
        current_score = max(self.scores[i] for i in range(len(self.scores)) if self.dinos[i].alive) if any(d.alive for d in self.dinos) else 0

        self.draw_text_on(surface, f"{self.experiment_config.label}", 10, 10)
        self.draw_text_on(surface, f"Gen: {self.generation}", 10, 40)
        self.draw_text_on(surface, f"Time: {elapsed:.1f}s", 10, 70)
        self.draw_text_on(surface, f"Alive: {alive_count}/{self.experiment_config.num_agents}", 10, 100)
        self.draw_text_on(surface, f"Score: {current_score}", 10, 130)

        self.screen.blit(surface, self.position)

    def draw_text_on(self, surface, text, x, y):
        label = self.font.render(text, True, (0, 0, 0))
        surface.blit(label, (x, y))