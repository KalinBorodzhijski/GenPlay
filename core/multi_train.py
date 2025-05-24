# multi_train.py

import time
import pygame
from core.agent import Agent
from core.ga import evolve_agents
from core.model_utils import save_best_agent

from games.flappy.core_game import GameCore as FlappyCore
from games.flappy import config as flappy_config

from games.dino.core_game import DinoCore
from games.dino.dino import Dino
from games.dino import config as dino_config

NUM_AGENTS = 2000
INPUT_SIZE = 5
MODEL_SAVE_PATH = "model/multigame_best.pkl"

def get_flappy_inputs(bird, pipe):
    dx = pipe.x - bird.x
    dy = (pipe.gap_y + pipe.gap_size / 2) - bird.y
    return [
        bird.y / flappy_config.SCREEN_HEIGHT,         # vertical position
        bird.velocity_y / 10.0,                       # vertical velocity
        dx / flappy_config.SCREEN_WIDTH,              # horizontal distance
        dy / flappy_config.SCREEN_HEIGHT,             # vertical distance to gap
        0.0                                           # Game ID
    ]

def get_dino_inputs(dino, obstacle):
    dx = (obstacle.x - dino.x) / dino_config.SCREEN_WIDTH if obstacle else 1.0
    obstacle_y = obstacle.y / dino_config.SCREEN_HEIGHT if obstacle else 0.0
    obstacle_height = obstacle.height / dino_config.SCREEN_HEIGHT if obstacle else 0.0
    y_vel = dino.velocity_y / 10.0

    return [
        0.0,                # Fake Y position (Dino doesn't use it)
        y_vel,              # Vertical velocity
        dx,                 # Distance to obstacle
        obstacle_y,         # Obstacle vertical position
        10.0                # Game ID
    ]

def evaluate_on_flappy(agents, bird_sprite, pipe_sprite):
    flappy = FlappyCore(bird_sprite, pipe_sprite, num_agents=NUM_AGENTS)
    scores = [0] * NUM_AGENTS
    MAX_SCORE = 200

    while flappy.alive and flappy.score < MAX_SCORE:
        print(f"Flappy Score: {flappy.score}", end="\r")
        next_pipe = None
        for pipe in flappy.pipes:
            if pipe.x + pipe.width > flappy.birds[0].x:
                next_pipe = pipe
                break

        decisions = []
        for i, bird in enumerate(flappy.birds):
            if not bird.alive:
                decisions.append(False)
                continue
            if next_pipe:
                inputs = get_flappy_inputs(bird, next_pipe)
            else:
                inputs = [bird.y / flappy_config.SCREEN_HEIGHT, bird.velocity_y / 10.0, 1.0, 0.0, 0.0]
            flappy_jump, _, _ = agents[i].decide(inputs)
            decisions.append(flappy_jump)
        flappy.update(agent_decisions=decisions)

    for i, bird in enumerate(flappy.birds):
        scores[i] = bird.score

    return scores

def evaluate_on_dino(agents):
    core = DinoCore()
    dinos = [Dino(50, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT - dino_config.DINO_HEIGHT) for _ in range(NUM_AGENTS)]
    scores = [0] * NUM_AGENTS

    MAX_SCORE = 200

    while any(d.alive for d in dinos) and max(d.score for d in dinos) < MAX_SCORE:
        print(f"Dino Score: {max(d.score for d in dinos)}", end="\r")
        core.update(dinos)

        next_obstacle = core.get_next_obstacle()
        for i, dino in enumerate(dinos):
            if not dino.alive:
                continue
            inputs = get_dino_inputs(dino, next_obstacle)
            _, dino_jump, duck = agents[i].decide(inputs)
            if dino_jump:
                dino.jump()
                dino.stand_up()
            elif duck:
                dino.duck()
            else:
                dino.stand_up()

            scores[i] = dino.score

    return scores

def multi_train(generations=1000):
    pygame.init()
    pygame.display.set_mode((1, 1))
    bird_sprite = pygame.image.load(flappy_config.BIRD_SPRITE).convert_alpha()
    pipe_sprite = pygame.image.load(flappy_config.PIPE_SPRITE).convert_alpha()

    agents = [Agent(INPUT_SIZE) for _ in range(NUM_AGENTS)]
    generation = 1

    while generation <= generations:
        print(f"\n=== Generation {generation} ===")

        # Evaluate on both games
        print("Evaluating on Flappy...")
        flappy_scores = evaluate_on_flappy(agents, bird_sprite, pipe_sprite)
        print("Evaluating on Dino...")
        dino_scores = evaluate_on_dino(agents)

        # Combine fitness
        combined = [min(f, d) for f, d in zip(flappy_scores, dino_scores)]

        # Save best
        best_index = max(range(NUM_AGENTS), key=lambda i: combined[i])
        save_best_agent(agents[best_index], combined[best_index], generation, save_path=MODEL_SAVE_PATH)

        # Evolve
        agents = evolve_agents(agents, combined)

        print(f"Best Fitness: {combined[best_index]:.2f}")
        generation += 1

    pygame.quit()

if __name__ == "__main__":
    multi_train()
# This script trains agents on both Flappy Bird and Dino games using a multi-game approach.
# It evaluates the agents on both games, combines their fitness scores, and evolves them over generations.