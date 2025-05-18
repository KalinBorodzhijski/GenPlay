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
        self.dino = Dino(50, config.SCREEN_HEIGHT - config.GROUND_HEIGHT - config.DINO_HEIGHT)
        self.obstacles = []
        self.last_spawn_time = pygame.time.get_ticks()
        self.next_spawn_delay = random.randint(config.MIN_OBSTACLE_DELAY, config.MAX_OBSTACLE_DELAY)
        self.score = 0
        self.alive = True
        self.game_speed = 6

    def spawn_obstacle(self):
        if self.obstacles and self.obstacles[-1].x > config.SCREEN_WIDTH - 200:
            return
        if random.random() < 0:
            self.obstacles.append(Obstacle(config.SCREEN_WIDTH, self.game_speed))
        else:
            self.obstacles.append(FlyingObstacle(config.SCREEN_WIDTH, self.game_speed))

    def update(self):
        if self.score % 5 == 0 and self.score != 0:
            self.game_speed += 0.02  # Gradual speed increase
        self.game_speed = min(self.game_speed, 13)  # Cap the speed

        self.dino.update()

        now = pygame.time.get_ticks()
        if now - self.last_spawn_time > self.next_spawn_delay:
            self.spawn_obstacle()
            self.last_spawn_time = now
            self.next_spawn_delay = random.randint(config.MIN_OBSTACLE_DELAY, config.MAX_OBSTACLE_DELAY)

        for obstacle in self.obstacles:
            obstacle.update()

        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        for obs in self.obstacles:
            if not obs.passed and obs.x + obs.width < self.dino.x:
                obs.passed = True
                self.score += 1

        if self.check_collision():
            self.dino.alive = False
            self.alive = False

    def check_collision(self):
        dino_bounds = self.dino.get_bounds()
        for obs in self.obstacles:
            o_bounds = obs.get_bounds()
            if (
                dino_bounds[2] > o_bounds[0] and dino_bounds[0] < o_bounds[2] and
                dino_bounds[3] > o_bounds[1] and dino_bounds[1] < o_bounds[3]
            ):
                return True
        return False

    def get_next_obstacle(self):
        for obs in self.obstacles:
            if obs.x + obs.width > self.dino.x:
                return obs
        return None