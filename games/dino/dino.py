import pygame
import games.dino.config as config

class Dino:
    """
    Represents the player-controlled dino character.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.on_ground = True
        self.alive = True
        self.is_ducking = False

        # Load and split spritesheet
        sheet = pygame.image.load(config.DINO_SPRITESHEET).convert_alpha()
        frame_width = sheet.get_width() // 24
        frame_height = sheet.get_height()
        scale_factor = 2.5

        # Running frames (1–10)
        run_indices = list(range(1, 11))
        self.run_frames = [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)),
                (int(frame_width * scale_factor), int(frame_height * scale_factor))
            )
            for i in run_indices
        ]

        # Ducking frames (13–17)
        duck_indices = list(range(13, 18))
        self.duck_frames = [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)),
                (int(frame_width * scale_factor), int(frame_height * scale_factor * 0.6))  # scale shorter
            )
            for i in duck_indices
        ]

        self.frames = self.run_frames
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_interval = 100  # ms

        self.width = self.frames[0].get_width()
        self.height = self.frames[0].get_height()
        self.original_height = self.height

        self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height


    def duck(self):
        if not self.is_ducking:
            self.is_ducking = True
            self.frames = self.duck_frames
            self.current_frame = 0
            self.height = self.frames[0].get_height()
            self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height

    def stand_up(self):
        if self.is_ducking:
            self.is_ducking = False
            self.frames = self.run_frames
            self.current_frame = 0
            self.height = self.frames[0].get_height()
            self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height


    def update(self):
        # Gravity
        if not self.on_ground:
            self.velocity_y += config.GRAVITY
            self.y += self.velocity_y

            if self.y >= config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height:
                self.y = config.SCREEN_HEIGHT - config.GROUND_HEIGHT - self.height
                self.velocity_y = 0
                self.on_ground = True

        # Animation
        self.animation_timer += pygame.time.get_ticks() % config.FPS
        if self.animation_timer > self.frame_interval:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Keyboard duck check (spacebar = duck for now)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.on_ground:
            self.duck()
        elif not keys[pygame.K_SPACE] and self.is_ducking:
            self.stand_up()


    def jump(self):
        if self.on_ground:
            self.velocity_y = config.JUMP_VELOCITY
            self.on_ground = False

    def get_bounds(self):
        padding_x = 4  # horizontal padding
        padding_y = 2  # vertical padding
        return (
            self.x + padding_x,
            self.y + padding_y,
            self.x + self.width - padding_x,
            self.y + self.height - padding_y
        )

    def draw(self, screen):
        screen.blit(self.frames[self.current_frame], (self.x, self.y))