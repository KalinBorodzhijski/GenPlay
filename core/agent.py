"""
agent.py

Defines the Agent class, which represents an AI-controlled player using a 
simple feedforward neural network. The agent makes binary decisions (jump or not) 
based on input features extracted from the game state.

This agent is designed to be evolved using a genetic algorithm by optimizing
its neural network weights (genome).

All inputs should be normalized before being passed to the agent's decision function.
"""
import numpy as np
import core.config as config

class Agent:
    """
    Represents a neural network-based agent with weights
    that can be evolved using a genetic algorithm.
    """

    def __init__(self, input_size, hidden_size=config.HIDDEN_LAYER_ONE_UNITS, output_size=config.OUTPUT_SIZE):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # One hidden layer: input → hidden → output
        self.genome_size = (
            input_size * hidden_size +
            hidden_size +
            hidden_size * output_size +
            output_size
        )

        self.genome = np.random.uniform(-1, 1, self.genome_size)

        
    def clone_with_mutation(self, mutation_rate=0.05, mutation_strength=0.5):
        """
        Creates a mutated copy of this agent.

        :param mutation_rate: Chance to mutate each gene
        :param mutation_strength: Max change per mutation
        :return: A new mutated Agent instance
        """
        new_agent = Agent(self.input_size)
        new_agent.genome = np.copy(self.genome)

        for i in range(len(new_agent.genome)):
            if np.random.rand() < mutation_rate:
                new_agent.genome[i] += np.random.uniform(-mutation_strength, mutation_strength)

        return new_agent
    
    def decide(self, inputs: list[float]) -> tuple[bool, bool, bool]:
        inputs = np.array(inputs)
        idx = 0

        # Hidden layer
        w1 = self.genome[idx:idx + self.input_size * self.hidden_size].reshape(self.hidden_size, self.input_size)
        idx += self.input_size * self.hidden_size
        b1 = self.genome[idx:idx + self.hidden_size]
        idx += self.hidden_size

        # Output layer
        w2 = self.genome[idx:idx + self.hidden_size * self.output_size].reshape(self.output_size, self.hidden_size)
        idx += self.hidden_size * self.output_size
        b2 = self.genome[idx:idx + self.output_size]

        # Forward pass
        h = np.tanh(np.dot(w1, inputs) + b1)
        output = self.sigmoid(np.dot(w2, h) + b2)

        flappy_jump = output[0] > 0.5
        dino_jump = output[1] > 0.5
        duck = output[2] > 0.5

        return flappy_jump, dino_jump, duck

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
