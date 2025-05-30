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
    Neural network agent with shared hidden layer and two output heads:
    - Flappy head: output[0] = jump
    - Dino head: output[1] = jump, output[2] = duck
    """

    def __init__(self, input_size, hidden_size=config.HIDDEN_LAYER_ONE_UNITS):
        self.input_size = input_size + 2  # Add 2 for one-hot game encoding
        self.hidden_size = hidden_size

        # Output sizes
        self.flappy_output_size = 1
        self.dino_output_size = 2

        
        # Genome layout:
        # Input → Hidden
        self.w1_size = self.input_size * self.hidden_size
        self.b1_size = self.hidden_size

        # Hidden → Flappy Output
        self.wf_size = self.hidden_size * self.flappy_output_size
        self.bf_size = self.flappy_output_size

        # Hidden → Dino Output
        self.wd_size = self.hidden_size * self.dino_output_size
        self.bd_size = self.dino_output_size

        self.genome_size = (
            self.w1_size + self.b1_size +
            self.wf_size + self.bf_size +
            self.wd_size + self.bd_size
        )

        self.genome = np.random.uniform(-1, 1, self.genome_size)


        
    def clone_with_mutation(self, mutation_rate=0.05, mutation_strength=0.5):
        """
        Creates a mutated copy of this agent.

        :param mutation_rate: Chance to mutate each gene
        :param mutation_strength: Max change per mutation
        :return: A new mutated Agent instance
        """
        new_agent = Agent(self.input_size - 2, self.hidden_size)
        new_agent.genome = np.copy(self.genome)

        for i in range(len(new_agent.genome)):
            if np.random.rand() < mutation_rate:
                new_agent.genome[i] += np.random.uniform(-mutation_strength, mutation_strength)

        return new_agent
    
    def decide(self, inputs: list[float]) -> tuple[bool, bool, bool]:
        """
        Expects inputs including one-hot game encoding as last 2 elements: [features..., is_flappy, is_dino]
        Returns a tuple: (flappy_jump, dino_jump, duck)
        """
        inputs = np.array(inputs)
        idx = 0

        # Shared hidden layer
        w1 = self.genome[idx:idx + self.w1_size].reshape(self.hidden_size, self.input_size)
        idx += self.w1_size
        b1 = self.genome[idx:idx + self.b1_size]
        idx += self.b1_size

        hidden = np.tanh(np.dot(w1, inputs) + b1)

        # Determine game from one-hot input
        is_flappy = inputs[-2] == 1.0
        is_dino = inputs[-1] == 1.0

        flappy_jump = dino_jump = duck = False

        if is_flappy:
            wf = self.genome[idx:idx + self.wf_size].reshape(self.flappy_output_size, self.hidden_size)
            idx += self.wf_size
            bf = self.genome[idx:idx + self.bf_size]
            idx += self.bf_size

            output = self.sigmoid(np.dot(wf, hidden) + bf)
            flappy_jump = output[0] > 0.5

        elif is_dino:
            idx += self.wf_size + self.bf_size  # skip flappy weights

            wd = self.genome[idx:idx + self.wd_size].reshape(self.dino_output_size, self.hidden_size)
            idx += self.wd_size
            bd = self.genome[idx:idx + self.bd_size]
            idx += self.bd_size

            output = self.sigmoid(np.dot(wd, hidden) + bd)
            dino_jump = output[0] > 0.5
            duck = output[1] > 0.5

        return flappy_jump, dino_jump, duck

    def decide_with_activations(self, inputs: list[float]) -> tuple[bool, bool, bool, dict]:
        """
        Like decide(), but also returns a dict of activations for visualization.
        """
        inputs = np.array(inputs)
        activations = {'input': inputs}
        idx = 0

        # Shared hidden layer
        w1 = self.genome[idx:idx + self.w1_size].reshape(self.hidden_size, self.input_size)
        idx += self.w1_size
        b1 = self.genome[idx:idx + self.b1_size]
        idx += self.b1_size

        hidden = np.tanh(np.dot(w1, inputs) + b1)
        activations['hidden'] = hidden
        activations['w1'] = w1

        # Determine game from one-hot input
        is_flappy = inputs[-2] == 1.0
        is_dino = inputs[-1] == 1.0

        flappy_jump = dino_jump = duck = False

        if is_flappy:
            wf = self.genome[idx:idx + self.wf_size].reshape(self.flappy_output_size, self.hidden_size)
            idx += self.wf_size
            bf = self.genome[idx:idx + self.bf_size]
            idx += self.bf_size

            output = self.sigmoid(np.dot(wf, hidden) + bf)
            flappy_jump = output[0] > 0.5
            activations['output'] = output
            activations['w_output'] = wf

        elif is_dino:
            idx += self.wf_size + self.bf_size  # skip flappy weights

            wd = self.genome[idx:idx + self.wd_size].reshape(self.dino_output_size, self.hidden_size)
            idx += self.wd_size
            bd = self.genome[idx:idx + self.bd_size]
            idx += self.bd_size

            output = self.sigmoid(np.dot(wd, hidden) + bd)
            dino_jump = output[0] > 0.5
            duck = output[1] > 0.5
            activations['output'] = output
            activations['w_output'] = wd

        return flappy_jump, dino_jump, duck, activations

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))