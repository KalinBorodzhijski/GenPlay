import pygame
import time
import games.dino.config as dino_config
from games.dino.dino import Dino
from games.dino.core_game import DinoCore
from core.agent import Agent
from core.ga import evolve_agents
from core.model_utils import *



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
            obstacle_y = obstacle.y / dino_config.SCREEN_HEIGHT
            obstacle_height = obstacle.height / dino_config.SCREEN_HEIGHT
        else:
            dx = 1.0
            obstacle_y = 0.0
            obstacle_height = 0.0

        y_vel = dino.velocity_y / 10.0

        return [
            0.0,         # Fake vertical position for Dino
            y_vel,       # Vertical velocity
            dx,          # Horizontal distance
            obstacle_y,  # Vertical distance (or use height if more useful)
            0.0, 1.0     # One-hot: [Flappy, Dino]
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

            core.update([dino])  # update game world with the single dino

            # Get next obstacle
            next_obstacle = core.get_next_obstacle()

            # Build input vector
            inputs = self.get_inputs(dino, next_obstacle)

            _, dino_jump, duck = agent.decide(inputs)
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

            pygame.display.flip()

            if not dino.alive:
                pygame.time.wait(1500)
                running = False

        pygame.quit()