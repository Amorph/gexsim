from collections import namedtuple

import math

from genetic.common import DNASequences, DNA
from genetic.dna import DNASequence
from genetic.float import encode as float_encode, decode as float_decode
from nn.nodes import NeuralNetwork, NeuralNetworkLayer, NeuralNetworkNeuron

NeuronDNAConnection = namedtuple('NeuronDNAConnection', ['neuron', 'link_data', 'weight'])

__ROUND_VALUE = 0.5
__NEURON_INDEX_REMAP = 0.99


def _create_layer(dna: DNASequence, network: NeuralNetwork, layer: NeuralNetworkLayer):
    dna.extend(DNASequences.NEURON_CREATE_LAYER)
    for neuron in layer.neurons:
        _create_neuron(dna, network, neuron)


def _create_neuron(dna: DNASequence, network: NeuralNetwork, neuron: NeuralNetworkNeuron):
    dna.extend(DNASequences.NEURON_CREATE)
    neuron_layer_index = network.layers.index(neuron.layer)
    # write bias
    float_encode(dna, neuron.bias)
    for connection in neuron.connections:
        dna.extend(DNASequences.NEURON_CREATE_LINK)
        node = connection.node  # type: NeuralNetworkNeuron
        layer_size = len(node.layer.neurons) - 1

        if layer_size == 0:
            layer_size = 1
        node_index = node.layer.neurons.index(node) / layer_size * __NEURON_INDEX_REMAP

        if node.layer == network.input:
            link_layer_index = -1
        else:
            link_layer_index = network.layers.index(node.layer)
        relative_index = neuron_layer_index - link_layer_index - 1
        float_encode(dna, relative_index + node_index)
        float_encode(dna, connection.weight)


def decompile(network: NeuralNetwork):
    dna = DNASequence()
    for layer in network.layers:
        _create_layer(dna, network, layer)

    return dna


def assemble(dna: DNASequence, network: NeuralNetwork):
    connections = []
    while not dna.finish:
        c = dna.any(DNASequences.NEURON_CREATE_LAYER, DNASequences.NEURON_CREATE, DNASequences.NEURON_CREATE_LINK)
        if c == DNASequences.NEURON_CREATE_LAYER:
            # skip layer creation if previous empty
            if network.layers and not network.layers[-1].neurons:
                continue
            network.layers.append(NeuralNetworkLayer(0))
        elif c == DNASequences.NEURON_CREATE:
            if not network.layers:
                continue
            current_layer = network.layers[-1]
            bias = float_decode(dna)
            neuron = NeuralNetworkNeuron(current_layer)
            neuron.bias = bias
            current_layer.neurons.append(neuron)
        elif c == DNASequences.NEURON_CREATE_LINK:
            if not network.layers or not network.layers[-1].neurons:
                continue
            neuron = network.layers[-1].neurons[-1]
            link_data = float_decode(dna)
            weight = float_decode(dna)
            connections.append(NeuronDNAConnection(neuron, link_data, weight))

    while not network.layers[-1].neurons:
        del network.layers[-1]
    network.outputs = network.layers[-1]

    layers = list()
    layers.append(network.input)
    layers.extend(network.layers)

    for connection in connections:
        neuron = connection.neuron  # type: NeuralNetworkNeuron
        layer_index = layers.index(neuron.layer)
        link_neuron_address, link_layer_address = math.modf(connection.link_data)

        layer_index -= math.trunc(link_layer_address + __ROUND_VALUE) + 1
        if len(layers) >= layer_index < 0:
            continue

        link_layer = layers[layer_index]  # type: NeuralNetworkLayer
        link_neuron_index = (len(link_layer.neurons)-1) * (link_neuron_address / __NEURON_INDEX_REMAP)
        neuron.add_connection(link_layer.neurons[math.trunc(link_neuron_index + __ROUND_VALUE)], connection.weight)
