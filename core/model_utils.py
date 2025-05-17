import pickle
import numpy as np
import os
from core.agent import Agent
from games.flappy import config

SAVE_PATH = os.path.join(config.SAVE_MODEL_PATH)

def save_best_agent(agent: Agent, fitness: float, generation: int):
    """
    Saves the best agent to disk if it's better than the previous one.
    """
    os.makedirs('model', exist_ok=True)
    best = load_best_agent()
    if best is None or fitness > best['fitness']:
        data = {
            "genome": agent.genome.tolist(),
            "fitness": fitness,
            "generation": generation
        }
        with open(config.SAVE_MODEL_PATH, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved new best agent (Gen {generation}, Fitness {fitness:.2f})")

def load_best_agent() -> dict | None:
    """
    Loads the best agent from disk, or returns None if not found.
    """
    if not os.path.exists(config.SAVE_MODEL_PATH):
        return None

    with open(config.SAVE_MODEL_PATH, "rb") as f:
        data = pickle.load(f)
        return data

def create_agent_from_genome(genome: list[float], input_size: int, hidden_size: int = 4) -> Agent:
    """
    Creates an agent with the given genome.
    """
    agent = Agent(input_size, hidden_size)
    agent.genome = np.array(genome)
    return agent