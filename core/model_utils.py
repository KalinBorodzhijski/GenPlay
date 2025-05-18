import pickle
import numpy as np
import os
from core.agent import Agent


def save_best_agent(agent: Agent, fitness: float, generation: int, save_path: str):
    """
    Saves the best agent to disk if it's better than the previously saved one.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    best = load_best_agent(save_path)

    if best is None or fitness > best['fitness']:
        data = {
            "genome": agent.genome.tolist(),
            "fitness": fitness,
            "generation": generation
        }
        with open(save_path, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved new best agent (Gen {generation}, Fitness {fitness:.2f})")


def load_best_agent(save_path: str) -> dict | None:
    """
    Loads the best agent from the given path, or returns None if not found.
    """
    if not os.path.exists(save_path):
        return None

    with open(save_path, "rb") as f:
        return pickle.load(f)

def create_agent_from_genome(genome: list[float], input_size: int, hidden_size: int = 4) -> Agent:
    """
    Creates an agent from a genome (used in replay/view mode).
    """
    agent = Agent(input_size, hidden_size)
    agent.genome = np.array(genome)
    return agent