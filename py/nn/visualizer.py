from nn.nodes import NeuralNetwork
from utils.vector2 import Vector2
from utils.vector3 import Vector3
from view.base import BaseView


def draw_network(view: BaseView, network: NeuralNetwork, options: dict):
    origin = Vector2() if 'origin' not in options else options['origin']
    size = Vector2(150, 100) if 'size' not in options else options['size']
    neuron_size = 1.0 if 'neuron_size' not in options else options['neuron_size']

    rect_color = Vector3(1.0, 1.0, 1.0)
    neuron_color = Vector3(0, 0, 1.0)

    view.draw_line(Vector2(origin.x, origin.y), Vector2(origin.x + size.x, origin.y), rect_color)
    view.draw_line(Vector2(origin.x + size.x, origin.y), Vector2(origin.x + size.x, origin.y + size.y), rect_color)
    view.draw_line(Vector2(origin.x + size.x, origin.y + size.y), Vector2(origin.x, origin.y + size.y), rect_color)
    view.draw_line(Vector2(origin.x, origin.y + size.y), Vector2(origin.x, origin.y), rect_color)

    layers = list()
    layers.append(network.input)
    layers.extend(network.layers)

    max_neurons_in_layer = len(layers[0].neurons)
    for layer in layers:
        if max_neurons_in_layer < len(layer.neurons):
            max_neurons_in_layer = len(layer.neurons)

    layer_width = size.x / (len(layers))
    neuron_vertical_space = size.y / max_neurons_in_layer

    def get_neuron_position(lindex, nindex):
        layer = layers[lindex]
        layer_position = origin + Vector2(layer_width * lindex, 0.0)
        layer_size_offset = Vector2(0, max_neurons_in_layer - len(layer.neurons)) * neuron_vertical_space
        neuron_position = layer_position + Vector2(0, neuron_vertical_space * nindex)
        neuron_position += layer_size_offset * 0.5
        return neuron_position

    connection_index = lambda connection: (layers.index(connection.node.layer),
                                           connection.node.layer.neurons.index(connection.node), )

    for layer_index, layer in enumerate(layers):
        for neuron_index, neuron in enumerate(layer.neurons):
            neuron_position = get_neuron_position(layer_index, neuron_index)
            view.draw_quad(neuron_position, Vector2(neuron_size, neuron_size), neuron_color)
            for connection in neuron.connections:
                connected_neuron_layer, connected_neuron_index = connection_index(connection)
                connected_neuron_position = get_neuron_position(connected_neuron_layer, connected_neuron_index)
                view.draw_line(connected_neuron_position + (neuron_size * 0.5),
                               neuron_position + (neuron_size * 0.5), rect_color)
