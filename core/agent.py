"""
agent.py

Defines the Agent class, which represents an AI-controlled player using a 
simple feedforward neural network. The agent makes binary decisions (jump or not) 
based on input features extracted from the game state.

This agent is designed to be evolved using a genetic algorithm by optimizing
its neural network weights (genome).

Input features from the game (Flappy Bird) expected by the agent:
1. Bird's vertical position (Y)
2. Bird's vertical velocity
3. Horizontal distance to the next pipe
4. Vertical distance between the bird and the center of the next pipe's gap

All inputs should be normalized before being passed to the agent's decision function.
"""
import numpy as np
import core.config as config

class Agent:
    """
    Represents a neural network-based agent with weights
    that can be evolved using a genetic algorithm.
    """

    def __init__(self, input_size: int, hidden_size: int = config.HIDDEN_LAYER_ONE_UNITS, output_size: int = 2):
        """
        Initializes an agent with random weights for a single-hidden-layer network.

        :param input_size: Number of input neurons
        :param hidden_size: Number of neurons in the hidden layer
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

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
        new_agent = Agent(self.input_size, self.hidden_size, self.output_size)
        new_agent.genome = np.copy(self.genome)

        for i in range(len(new_agent.genome)):
            if np.random.rand() < mutation_rate:
                new_agent.genome[i] += np.random.uniform(-mutation_strength, mutation_strength)

        return new_agent

    def decide(self, inputs: list[float]) -> tuple[bool, bool]:
        """
        Feedforward neural network: decide actions.

        :param inputs: 5 normalized features
        :return: (jump: bool, duck: bool)
        """
        inputs = np.array(inputs)

        idx = 0
        w1 = self.genome[idx:idx + self.input_size * self.hidden_size].reshape(self.hidden_size, self.input_size)
        idx += self.input_size * self.hidden_size

        b1 = self.genome[idx:idx + self.hidden_size]
        idx += self.hidden_size

        w2 = self.genome[idx:idx + self.hidden_size * self.output_size].reshape(self.output_size, self.hidden_size)
        idx += self.hidden_size * self.output_size

        b2 = self.genome[idx:idx + self.output_size]

        # Feedforward
        hidden = np.tanh(np.dot(w1, inputs) + b1)
        output = np.dot(w2, hidden) + b2  # no activation to allow thresholding

        jump = output[0] > 0.5
        duck = output[1] > 0.5

        return jump, duck