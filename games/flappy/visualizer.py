import pygame
import time
from games.flappy import config
from games.flappy.core_game import GameCore
from core.agent import Agent
from core.model_utils import save_best_agent, load_best_agent, create_agent_from_genome
from core.ga import evolve_agents

from core.network_visualization import draw_network_visualization
from core.experiments.experiment_config import ExperimentConfig


INPUT_SIZE = 10

class VisualTrainer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Training Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.background = pygame.image.load(config.BG_IMAGE).convert()
        self.background = pygame.transform.scale(self.background, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        self.bird_sprite = pygame.image.load(config.BIRD_SPRITE).convert_alpha()
        self.pipe_sprite_sheet = pygame.image.load(config.PIPE_SPRITE).convert_alpha()

        self.generation = 1
        self.start_time = time.time()

        self.engine = GameCore(self.bird_sprite, self.pipe_sprite_sheet, config.NUM_AGENTS)

        self.agents = []
        self.reset_generation()

    def reset_generation(self):
        """
        Resets all agents and birds for a new generation.
        Also handles fitness evaluation and saves the best agent.
        """
        if self.agents:
            self.fitness_scores = []
            for bird in self.engine.birds:
                fitness = bird.score
                self.fitness_scores.append(fitness)

            best_index = max(range(len(self.agents)), key=lambda i: self.fitness_scores[i])
            best_fitness = self.fitness_scores[best_index]
            best_agent = self.agents[best_index]

            save_best_agent(best_agent, best_fitness, self.generation, config.SAVE_MODEL_PATH)

            self.agents = evolve_agents(self.agents, self.fitness_scores)

        else:
            self.agents = [Agent(INPUT_SIZE) for _ in range(config.NUM_AGENTS)]

        self.engine.reset()


    def run(self):
        running = True
        while running:
            self.clock.tick(config.FPS)
            running = self.handle_events()

            self.update()   # Uses agents to make decisions and update the game
            self.draw()

            # When all birds are dead, evolve to next generation
            if all(not bird.alive for bird in self.engine.birds):
                self.generation += 1
                self.reset_generation()

        pygame.quit()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for bird in self.engine.birds:
            if bird.alive:
                bird.draw(self.screen)

        for pipe in self.engine.pipes:
            pipe.draw(self.screen)

        elapsed = time.time() - self.start_time
        alive_count = sum(1 for bird in self.engine.birds if bird.alive)


        self.draw_text(f"Generation: {self.generation}", 10, 10)
        self.draw_text(f"Training Time: {elapsed:.1f}s", 10, 40)
        self.draw_text(f"Score: {self.engine.score}", 10, 70)
        self.draw_text(f"Alive: {alive_count} / {len(self.engine.birds)}", 10, 100)

        pygame.display.flip()

    def draw_text(self, text, x, y):
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, (x, y))


    def get_inputs(self, bird, next_pipe):
        if next_pipe:
            dx = (next_pipe.x - bird.x) / config.SCREEN_WIDTH
            dy = ((next_pipe.gap_y + next_pipe.gap_size / 2) - bird.y) / config.SCREEN_HEIGHT
            gap_size = next_pipe.gap_size / config.SCREEN_HEIGHT
            pipe_speed = next_pipe.speed / config.PIPE_SPEED
            time_to_pipe = dx / (next_pipe.speed + 1e-5)
        else:
            dx = 1.0
            dy = 0.0
            gap_size = 0.0
            pipe_speed = 1.0
            time_to_pipe = 1.0

        return [
            bird.y / config.SCREEN_HEIGHT, 
            bird.velocity_y / 10.0,
            dx,
            dy,
            gap_size, 
            pipe_speed,
            time_to_pipe,
            0.0,                                  # unused for Flappy
            0.0,                                  # unused for Flappy
            0.0,                                  # unused for Flappy
            1.0,                                  # One-hot: Flappy
            0.0                                   # One-hot: not Dino
        ]


    def find_next_pipe(self):
        """
        Returns the next pipe (closest ahead of the bird).
        """
        for pipe in self.engine.pipes:
            if pipe.x + pipe.width > self.engine.birds[0].x:
                return pipe
        return self.engine.pipes[0] if self.engine.pipes else None
        
    def update(self):
        next_pipe = self.find_next_pipe()
        decisions = []
        best_score = 0
        best_index = -1
        for i, bird in enumerate(self.engine.birds):
            if not bird.alive:
                decisions.append(False)
                continue

            agent = self.agents[i]
            inputs = self.get_inputs(bird, next_pipe)
            flappy_jump, _, _ = agent.decide(inputs)
            decisions.append(flappy_jump)

            if bird.score > best_score:
                best_score = bird.score
                best_index = i

        if best_score % 50 == 0 and best_score != 0:
            best_agent = self.agents[best_index]
            save_best_agent(best_agent, best_score, self.generation, config.SAVE_MODEL_PATH)
            print(f"[Checkpoint] Saved agent at score {best_score}")


        self.engine.update(agent_decisions=decisions)

    def watch_best(self, model_path=None):
        """
        Loads and plays the best saved agent.
        :param model_path: Path to the saved model. If None, uses the default path.
        """
        visualizer_enabled = False
        path = model_path if model_path else config.SAVE_MODEL_PATH
        best = load_best_agent(path)
        if not best:
            print("No saved agent found.")
            return

        agent = create_agent_from_genome(best["genome"], input_size=INPUT_SIZE)
        engine = GameCore(self.bird_sprite, self.pipe_sprite_sheet, num_agents=1)
        bird = engine.birds[0]

        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        visualizer_enabled = not visualizer_enabled

            next_pipe = self.find_next_pipe_for_bird(bird, engine.pipes)

            inputs = self.get_inputs(bird, next_pipe)

            flappy_jump, _, _, activations = agent.decide_with_activations(inputs)
            if flappy_jump:
                bird.jump()

            engine.update(agent_decisions=[False])

            self.screen.blit(self.background, (0, 0))
            for pipe in engine.pipes:
                pipe.draw(self.screen)
            bird.draw(self.screen)

            self.draw_text(f"Best Agent - Gen {best['generation']} / Fitness: {best['fitness']}", 10, 10)
            self.draw_text(f"Score: {engine.score}", 10, 40)
            input_labels = [
                "Bird Y",              # 1
                "Vertical Velocity",   # 2
                "Distance to Pipe",    # 3
                "Distance to Gap Center",  # 4
                "Gap Size",            # 5
                "Pipe Speed",          # 6
                "Time to Pipe",        # 7
                "Unused (0)",          # 8
                "Unused (0)",          # 9
                "Unused (0)",          #10
                "Flappy Game",         #11
                "Dino Game"            #12
            ]

            output_labels = ["Flappy Jump"]

            if visualizer_enabled:
                draw_network_visualization(
                    self.screen,
                    activations,
                    input_labels=input_labels,
                    output_labels=output_labels
                )
            pygame.display.flip()

            if not bird.alive:
                pygame.time.wait(1500)
                running = False

        pygame.quit()

    def find_next_pipe_for_bird(self, bird, pipes):
        for pipe in pipes:
            if pipe.x + pipe.width > bird.x:
                return pipe
        return pipes[0] if pipes else None
    
class FlappyVisualizerWithConfig(VisualTrainer):
    def __init__(self, experiment_config: ExperimentConfig, shared_screen):
        self.experiment_config = experiment_config
        self.screen = shared_screen
        self.position = experiment_config.position
        self.mutation_rate = experiment_config.mutation_rate
        self.retain_top = experiment_config.retain_top
        config.NUM_AGENTS = experiment_config.num_agents

        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.background = pygame.image.load(config.BG_IMAGE).convert()
        self.background = pygame.transform.scale(self.background, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        self.bird_sprite = pygame.image.load(config.BIRD_SPRITE).convert_alpha()
        self.pipe_sprite_sheet = pygame.image.load(config.PIPE_SPRITE).convert_alpha()

        self.generation = 1
        self.start_time = time.time()

        self.engine = GameCore(self.bird_sprite, self.pipe_sprite_sheet, experiment_config.num_agents)

        self.agents = []
        self.reset_generation()

    def reset_generation(self):
        if self.agents:
            self.fitness_scores = [bird.score for bird in self.engine.birds]
            best_index = max(range(len(self.agents)), key=lambda i: self.fitness_scores[i])
            self.agents = evolve_agents(
                self.agents, self.fitness_scores,
                retain_top=self.retain_top,
                mutate_rate=self.mutation_rate
            )
        else:
            self.agents = [Agent(INPUT_SIZE) for _ in range(self.experiment_config.num_agents)]
        self.engine.reset()

    def update(self):
        next_pipe = self.find_next_pipe()
        decisions = []
        best_score = 0
        best_index = -1

        for i, bird in enumerate(self.engine.birds):
            if not bird.alive:
                decisions.append(False)
                continue

            agent = self.agents[i]
            inputs = self.get_inputs(bird, next_pipe)
            flappy_jump, _, _ = agent.decide(inputs)
            decisions.append(flappy_jump)

            if bird.score > best_score:
                best_score = bird.score
                best_index = i

        self.engine.update(agent_decisions=decisions)

        if all(not bird.alive for bird in self.engine.birds):
            self.generation += 1
            self.reset_generation()

    def draw(self):
        surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        surface.blit(self.background, (0, 0))

        for bird in self.engine.birds:
            if bird.alive:
                bird.draw(surface)

        for pipe in self.engine.pipes:
            pipe.draw(surface)

        elapsed = time.time() - self.start_time
        alive_count = sum(1 for bird in self.engine.birds if bird.alive)

        self.draw_text_on(surface, f"{self.experiment_config.label}", 10, 10)
        self.draw_text_on(surface, f"Gen: {self.generation}", 10, 40)
        self.draw_text_on(surface, f"Time: {elapsed:.1f}s", 10, 70)
        self.draw_text_on(surface, f"Alive: {alive_count}/{self.experiment_config.num_agents}", 10, 100)
        self.draw_text_on(surface, f"Score: {self.engine.score}", 10, 130)

        self.screen.blit(surface, self.position)

    def draw_text_on(self, surface, text, x, y):
        label = self.font.render(text, True, (0, 0, 0))
        surface.blit(label, (x, y))