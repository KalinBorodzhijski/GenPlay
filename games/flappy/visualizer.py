import pygame
import time
from games.flappy import config
from games.flappy.core_game import GameCore
from core.agent import Agent
from core.model_utils import save_best_agent, load_best_agent, create_agent_from_genome
from core.ga import evolve_agents

INPUT_SIZE = 5

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
            # Calculate fitness as score (can be improved later)
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
        """
        Returns a normalized input vector for the neural network.

        :param bird: Bird object
        :param next_pipe: Pipe object
        :return: List of 4 float values
        """
        dx = next_pipe.x - bird.x
        dy = (next_pipe.gap_y + next_pipe.gap_size / 2) - bird.y

        inputs = [
            bird.y / config.SCREEN_HEIGHT,
            bird.velocity_y / 10.0,            # assuming max velocity ~10
            dx / config.SCREEN_WIDTH,
            dy / config.SCREEN_HEIGHT,
            0
        ]
        return inputs


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
        for i, bird in enumerate(self.engine.birds):
            if not bird.alive:
                decisions.append(False)
                continue

            agent = self.agents[i]

            if next_pipe is not None:
                inputs = self.get_inputs(bird, next_pipe)
            else:
                inputs = [bird.y / config.SCREEN_HEIGHT, bird.velocity_y / 10.0, 1.0, 0.0, 0.0]

            flappy_jump, _, _ = agent.decide(inputs)
            decisions.append(flappy_jump)

        self.engine.update(agent_decisions=decisions)

    def watch_best(self, model_path=None):
        """
        Loads and plays the best saved agent.
        :param model_path: Path to the saved model. If None, uses the default path.
        """
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

            next_pipe = self.find_next_pipe_for_bird(bird, engine.pipes)

            if next_pipe:
                inputs = self.get_inputs(bird, next_pipe)
            else:
                inputs = [bird.y / config.SCREEN_HEIGHT, bird.velocity_y / 10.0, 1.0, 0.0, 0.0]

            flappy_jump, _, _ = agent.decide(inputs)
            if flappy_jump:
                bird.jump()

            engine.update(agent_decisions=[False])

            self.screen.blit(self.background, (0, 0))
            for pipe in engine.pipes:
                pipe.draw(self.screen)
            bird.draw(self.screen)

            self.draw_text(f"Best Agent - Gen {best['generation']} / Fitness: {best['fitness']}", 10, 10)
            self.draw_text(f"Score: {engine.score}", 10, 40)

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