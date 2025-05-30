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
from games.dino.obstacles import FlyingObstacle
from games.dino import config as dino_config

NUM_AGENTS = 2000
INPUT_SIZE = 10
MODEL_SAVE_PATH = "model/multigame_best.pkl"

def get_flappy_inputs(bird, next_pipe):
    if next_pipe:
        dx = (next_pipe.x - bird.x) / flappy_config.SCREEN_WIDTH
        dy = ((next_pipe.gap_y + next_pipe.gap_size / 2) - bird.y) / flappy_config.SCREEN_HEIGHT
        gap_size = next_pipe.gap_size / flappy_config.SCREEN_HEIGHT
        pipe_speed = next_pipe.speed / flappy_config.PIPE_SPEED
        time_to_pipe = dx / (next_pipe.speed + 1e-5)
    else:
        dx = 1.0
        dy = 0.0
        gap_size = 0.0
        pipe_speed = 1.0
        time_to_pipe = 1.0

    return [
        bird.y / flappy_config.SCREEN_HEIGHT, 
        bird.velocity_y / 10.0,               
        dx,                                   
        dy,                                   
        gap_size,                             
        pipe_speed,                           
        time_to_pipe,                         
        0.0, 0.0, 0.0, 1.0, 0.0
    ]

def get_dino_inputs(dino, obstacle):
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
        dino.y / dino_config.SCREEN_HEIGHT,   # 1
        dino.velocity_y / 10.0,               # 2
        dx,                                   # 3
        dy,                                   # 4
        obstacle_height,                      # 5
        obstacle_width,                       # 6
        obstacle_speed,                       # 7
        time_to_collision,                    # 8
        is_flying,                            # 9
        is_ground,                            #10
        0.0,                                   #11 ← reserved for Flappy only
        1.0                                    #12 ← One-hot: Dino
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
            inputs = get_flappy_inputs(bird, next_pipe)
            
            flappy_jump, _, _ = agents[i].decide(inputs)
            decisions.append(flappy_jump)
        flappy.update(agent_decisions=decisions)

    for i, bird in enumerate(flappy.birds):
        scores[i] = bird.score * 100 + bird.time_alive / 10

    return scores

def evaluate_on_dino(agents):
    core = DinoCore()
    dinos = [Dino(50, dino_config.SCREEN_HEIGHT - dino_config.GROUND_HEIGHT - dino_config.DINO_HEIGHT) for _ in range(NUM_AGENTS)]
    scores = [0] * NUM_AGENTS

    MAX_SCORE = 100

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

            scores[i] = dino.score * 100

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
        combined = [f + d for f, d in zip(flappy_scores, dino_scores)]

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

