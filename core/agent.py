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

    def __init__(self, input_size, hidden1_size=config.HIDDEN_LAYER_ONE_UNITS, hidden2_size=config.HIDDEN_LAYER_TWO_UNITS, output_size=config.OUTPUT_SIZE):
        """
        Initializes an agent with random weights for a single-hidden-layer network.

        :param input_size: Number of input neurons
        :param hidden_size: Number of neurons in the hidden layer
        """
        self.input_size = input_size
        self.hidden1_size = hidden1_size
        self.hidden2_size = hidden2_size
        self.output_size = output_size

        self.genome_size = (
            input_size * hidden1_size +
            hidden1_size +
            hidden1_size * hidden2_size +
            hidden2_size +
            hidden2_size * output_size +
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
        new_agent = Agent(self.input_size, self.hidden1_size,self.hidden2_size , self.output_size)
        new_agent.genome = np.copy(self.genome)

        for i in range(len(new_agent.genome)):
            if np.random.rand() < mutation_rate:
                new_agent.genome[i] += np.random.uniform(-mutation_strength, mutation_strength)

        return new_agent
    
    def decide(self, inputs: list[float]) -> tuple[bool, bool, bool]:
        inputs = np.array(inputs)
        idx = 0

        # First hidden layer
        w1 = self.genome[idx:idx + self.input_size * self.hidden1_size].reshape(self.hidden1_size, self.input_size)
        idx += self.input_size * self.hidden1_size
        b1 = self.genome[idx:idx + self.hidden1_size]
        idx += self.hidden1_size

        # Second hidden layer
        w2 = self.genome[idx:idx + self.hidden1_size * self.hidden2_size].reshape(self.hidden2_size, self.hidden1_size)
        idx += self.hidden1_size * self.hidden2_size
        b2 = self.genome[idx:idx + self.hidden2_size]
        idx += self.hidden2_size

        # Output layer
        w3 = self.genome[idx:idx + self.hidden2_size * self.output_size].reshape(self.output_size, self.hidden2_size)
        idx += self.hidden2_size * self.output_size
        b3 = self.genome[idx:idx + self.output_size]

        # Forward pass
        h1 = np.tanh(np.dot(w1, inputs) + b1)
        h2 = np.tanh(np.dot(w2, h1) + b2)
        output = self.sigmoid(np.dot(w3, h2) + b3)

        flappy_jump = output[0] > 0.5
        dino_jump = output[1] > 0.5
        duck = output[2] > 0.5

        return flappy_jump, dino_jump, duck
        
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
