"""
core.py

Shared base game logic that will be used by the training and manual play
"""

import pygame
from games.flappy import config
from games.flappy.bird import Bird
from games.flappy.pipe import Pipe

class GameCore:
    """
    Core logic for the Flappy game, abstracted from rendering and input.
    Can support single or multiple birds.
    """

    def __init__(self, bird_sprite, pipe_sprite_sheet, num_agents=1):
        self.bird_sprite = bird_sprite
        self.pipe_sprite_sheet = pipe_sprite_sheet
        self.num_agents = num_agents

        self.reset()

    def reset(self):
        """
        Resets the game state.
        """
        self.birds = [Bird(80, config.SCREEN_HEIGHT // 2, self.bird_sprite) for _ in range(self.num_agents)]
        self.pipes = []
        self.last_pipe_time = pygame.time.get_ticks()
        self.score = 0
        self.alive = True


    def spawn_pipe(self):
        """
        Spawns a new pipe with randomized appearance.
        """
        col = pygame.time.get_ticks() // 1500 % 4
        row = (pygame.time.get_ticks() // 3000) % 2
        rect = pygame.Rect(
            col * config.IMAGE_PIPE_WIDTH,
            row * config.IMAGE_PIPE_HEIGHT,
            config.IMAGE_PIPE_WIDTH,
            config.IMAGE_PIPE_HEIGHT
        )
        pipe_img = self.pipe_sprite_sheet.subsurface(rect).copy()
        self.pipes.append(Pipe(config.SCREEN_WIDTH, pipe_img))

        
    def update(self, agent_decisions=None):
        """
        Updates game state.

        :param agent_decisions: List of bools; each True = jump. Used for AI control.
        """
        now = pygame.time.get_ticks()
        if now - self.last_pipe_time > config.PIPE_INTERVAL:
            self.spawn_pipe()
            self.last_pipe_time = now

        for pipe in self.pipes:
            pipe.update()
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

        all_dead = True

        for idx, bird in enumerate(self.birds):
            if not bird.alive:
                continue

            # Decision logic: agent or manual
            if agent_decisions and agent_decisions[idx]:
                bird.jump()

            bird.update()
            if self.check_collision(bird):
                bird.alive = False
            else:
                all_dead = False

        for pipe in self.pipes:
            if not pipe.passed and pipe.x + pipe.width < self.birds[0].x:
                pipe.passed = True
                for bird in self.birds:
                    if bird.alive:
                        bird.score += 1  # Give each surviving bird the score
                self.score += 1
                
        self.alive = not all_dead

    def check_collision(self, bird):
        """
        Collision detection for a single bird.
        """
        bounds = bird.get_bounds()
        for pipe in self.pipes:
            top, bottom = pipe.get_bounds()
            for rect in [top, bottom]:
                l, t, r, b = rect
                if (
                    bounds[2] > l and bounds[0] < r and
                    bounds[3] > t and bounds[1] < b
                ):
                    return True
        return bird.y < 0 or bird.y > config.SCREEN_HEIGHT