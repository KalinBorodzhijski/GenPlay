import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class ExperimentConfig:
    label: str
    mutation_rate: float
    retain_top: float
    num_agents: int
    game_type: str  # "dino" or "flappy"
    position: tuple = (0, 0)


