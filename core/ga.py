import numpy as np
from core.agent import Agent

def evolve_agents(old_agents: list[Agent], fitness_scores: list[float], retain_top: float, mutate_rate: float):
    """
    Evolves a population of agents using elitism and mutation.

    :param old_agents: List of agents from the previous generation
    :param fitness_scores: Corresponding fitness scores
    :param retain_top: Top X% of agents to keep
    :param mutate_rate: Chance of mutation
    :return: List of new agents
    """
    num_agents = len(old_agents)
    retain_length = max(1, int(num_agents * retain_top))

    # Sort agents by fitness (descending)
    sorted_indices = np.argsort(fitness_scores)[::-1]
    elites = [old_agents[i] for i in sorted_indices[:retain_length]]

    # Create new generation by cloning + mutating
    new_agents = elites.copy()
    while len(new_agents) < num_agents:
        parent = np.random.choice(elites)
        child = parent.clone_with_mutation(mutation_rate=mutate_rate)
        new_agents.append(child)

    return new_agents