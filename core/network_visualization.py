import pygame
import numpy as np


def draw_network_visualization(screen, activations, max_display_hidden=16, input_labels=None, output_labels=None):
    screen_width, screen_height = screen.get_size()

    node_radius = 10
    top_padding = 50
    bottom_padding = 50
    layer_horizontal_margin = 100

    # Extract activations
    input_vals = activations['input']
    hidden_vals = activations['hidden']
    output_vals = activations['output']
    w1 = activations['w1']
    w_output = activations['w_output']

    num_layers = 3
    total_layer_width = screen_width - 2 * layer_horizontal_margin
    layer_spacing = total_layer_width // (num_layers - 1)
    x_positions = [layer_horizontal_margin + i * layer_spacing for i in range(num_layers)]

    def get_y_positions(num_nodes):
        available_height = screen_height - top_padding - bottom_padding
        spacing = available_height / (num_nodes + 1)
        return [top_padding + (i + 1) * spacing for i in range(num_nodes)]

    def sample_layer(values, max_display):
        if len(values) <= max_display:
            return list(enumerate(values))
        step = len(values) / max_display
        return [(int(i * step), values[int(i * step)]) for i in range(max_display)]

    # Sample hidden neurons
    sampled_hidden = sample_layer(hidden_vals, max_display_hidden)
    hidden_indices, hidden_sample_vals = zip(*sampled_hidden) if sampled_hidden else ([], [])

    y_input = get_y_positions(len(input_vals))
    y_hidden = get_y_positions(len(hidden_sample_vals))
    y_output = get_y_positions(len(output_vals))

    # Draw connection lines
    def draw_connections(from_vals, to_vals, weights, x_from, x_to, y_from, y_to, from_indices=None, to_indices=None):
        for i, from_val in enumerate(from_vals):
            for j, to_val in enumerate(to_vals):
                src = from_indices[i] if from_indices else i
                tgt = to_indices[j] if to_indices else j
                weight = weights[tgt, src]
                color = (255, 0, 0) if weight > 0 else (0, 0, 255)
                pygame.draw.line(screen, color, (x_from, y_from[i]), (x_to, y_to[j]), 1)

    # Draw neurons
    def draw_layer(values, x, y_positions, labels=None):
        font = pygame.font.SysFont("Arial", 14)
        for i, val in enumerate(values):
            norm_val = max(min(val, 1.0), -1.0)
            intensity = int(255 * max(0, norm_val))
            color = (0, intensity, 0)
            pos = (x, int(y_positions[i]))
            pygame.draw.circle(screen, color, pos, node_radius)

            # Draw text if labels are provided
            if labels and i < len(labels):
                label_surface = font.render(labels[i], True, (0, 0, 0))
                screen.blit(label_surface, (x - node_radius - 70, y_positions[i] - 7))
    # Connections: input → sampled hidden
    draw_connections(
        input_vals, hidden_sample_vals, w1,
        x_positions[0], x_positions[1],
        y_input, y_hidden,
        from_indices=range(len(input_vals)),
        to_indices=hidden_indices
    )

    # Connections: sampled hidden → output
    draw_connections(
        hidden_sample_vals, output_vals, w_output,
        x_positions[1], x_positions[2],
        y_hidden, y_output,
        from_indices=hidden_indices,
        to_indices=None  # outputs aren't sampled
    )

    # Draw neurons
    draw_layer(input_vals, x_positions[0], y_input, labels=input_labels)
    draw_layer(hidden_sample_vals, x_positions[1], y_hidden, labels=None)
    draw_layer(output_vals, x_positions[2], y_output, labels=output_labels)