import pygame
import random
import games.dino.config as config
from games.dino.dino import Dino
from games.dino.obstacles import Obstacle, FlyingObstacle


class DinoCore:
    """
    Core game logic shared between interactive play and agent training.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.obstacles = []
        self.last_spawn_time = pygame.time.get_ticks()
        self.next_spawn_delay = random.randint(config.MIN_OBSTACLE_DELAY, config.MAX_OBSTACLE_DELAY)
        self.game_speed = config.BASE_SPEED
        self.speed_timer = pygame.time.get_ticks()

    def spawn_obstacle(self):
        if self.obstacles and self.obstacles[-1].x > config.SCREEN_WIDTH - 200:
            return
        if random.random() < 0.7:  # 70% chance to spawn a cactus
            self.obstacles.append(Obstacle(config.SCREEN_WIDTH, self.game_speed))
        else:
            self.obstacles.append(FlyingObstacle(config.SCREEN_WIDTH, self.game_speed))


    def update(self, dinos: list):
        # Gradually increase speed
        now = pygame.time.get_ticks()
        if now - self.speed_timer > 3000:
            self.game_speed += 0.1
            self.game_speed = min(self.game_speed, 12)
            self.speed_timer = now

        # Obstacle spawning
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time > self.next_spawn_delay:
            self.spawn_obstacle()
            self.last_spawn_time = now
            self.next_spawn_delay = random.randint(config.MIN_OBSTACLE_DELAY, config.MAX_OBSTACLE_DELAY)

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update()

        # Remove off-screen obstacles
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        # Process each dino
        for i, dino in enumerate(dinos):
            if not dino.alive:
                continue

            dino.update()

            # Track obstacles passed per dino
            for obs in self.obstacles:
                if not hasattr(obs, 'passed_by'):
                    obs.passed_by = set()

                if i not in obs.passed_by and obs.x + obs.width < dino.x:
                    obs.passed_by.add(i)
                    dino.score = getattr(dino, 'score', 0) + 1

            # Check for collision
            dino_bounds = dino.get_bounds()
            for obs in self.obstacles:
                o_bounds = obs.get_bounds()
                if (
                    dino_bounds[2] > o_bounds[0] and dino_bounds[0] < o_bounds[2] and
                    dino_bounds[3] > o_bounds[1] and dino_bounds[1] < o_bounds[3]
                ):
                    dino.alive = False

    def get_next_obstacle(self):
        for obs in self.obstacles:
            if obs.x + obs.width > 0:
                return obs
        return None