import random
from collections import namedtuple

Connection = namedtuple('Connection', ['node', 'weight'])


class NeuralNetworkNeuron:
    def __init__(self, layer):
        self.layer = layer
        self.value = 0.0
        self.bias = random.random() - 0.5
        self.connections = []

    def add_connection(self, neuron, weight: float):
        self.connections.append(Connection(neuron, weight))


class NeuralNetworkLayer:
    def __init__(self, count):
        self.neurons = []

        for i in range(count):
            self.neurons.append(NeuralNetworkNeuron(self))

    def connect(self, layer):
        for neuron in self.neurons:
            for baseNeuron in layer.neurons:
                neuron.add_connection(baseNeuron, random.random() * 2.0 - 1.0)


class NeuralNetwork:
    def __init__(self, inputs, outputs, hidden):
        self.input = NeuralNetworkLayer(inputs)
        self.layers = []

        previous_layer = self.input

        for count in hidden:
            hidden_layer = NeuralNetworkLayer(count)
            hidden_layer.connect(previous_layer)
            previous_layer = hidden_layer
            self.layers.append(hidden_layer)

        if outputs:
            self.outputs = NeuralNetworkLayer(outputs)
            self.outputs.connect(previous_layer)
            self.layers.append(self.outputs)

    def update(self, inputs):
        for i, neuron in enumerate(self.input.neurons):
            neuron.value = inputs[i]

        for layer in self.layers:
            for neuron in layer.neurons:
                neuron.value = neuron.bias
                for connection in neuron.connections:
                    neuron.value += connection.node.value * connection.weight
                if neuron.value > 1:
                    neuron.value = 1
                elif neuron.value < -1:
                    neuron.value = -1
        return [neuron.value for neuron in self.outputs.neurons]