import random
import gexnetpy as GN


class GNNet:
    @staticmethod
    def create_random(G, inputs, outputs, hidden_layer):
        nodes_count = inputs + outputs + hidden_layer
        links_count = inputs * hidden_layer + hidden_layer * outputs
        weights_data = [random.uniform(-1.0, 1.0) for _ in range(links_count)]
        bias_data = [random.uniform(-1.0, 1.0) for _ in range(nodes_count)]
        links_data = []

        for x in range(inputs):
            for y in range(hidden_layer):
                links_data.append((x, inputs + y,))
        for x in range(hidden_layer):
            for y in range(outputs):
                links_data.append((inputs + x, inputs + hidden_layer + y))

        assert len(links_data) == links_count

        links = G.create_stream_data(GN.GN_TYPE_LINK, links_data)
        assert nodes_count == G.compute_node_count(links)
        weights = G.create_stream_data(GN.GN_TYPE_NUMBER, weights_data)
        biases = G.create_stream_data(GN.GN_TYPE_NUMBER, bias_data)

        data0 = G.create_stream(GN.GN_TYPE_NUMBER, nodes_count)
        data1 = G.create_stream(GN.GN_TYPE_NUMBER, nodes_count)

        i, o = G.compute_in_out(links, nodes_count)

        data0.clear()
        data1.clear()

        return GNNet(G, {
            'in_out': (i, o),
            'links': links,
            'weights': weights,
            'biases': biases,
            'data': [data0, data1]
        })

    def __init__(self, G, data):
        self.G = G
        self._in_idx = data['in_out'][0]
        self._out_idx = data['in_out'][1]
        self._links = data['links']
        self._weights = data['weights']
        self._biases = data.get('biases')
        self._data = data['data']
        self._in_data = G.create_stream(GN.GN_TYPE_NUMBER, self._in_idx.count)
        self._out_data = G.create_stream(GN.GN_TYPE_NUMBER, self._out_idx.count)

    def process(self, inputs):
        assert len(inputs) == self._in_data.count

        self._in_data.set_stream_data(inputs)
        self._data[1].set_stream_data_indexed(self._in_idx, self._in_data)

        self._data[0].copy(self._biases)
        self._data[0].multiply_add_links(self._links, self._data[1], self._weights)
        self._data[1].process_stream(self._data[0], GN.GN_FUNCTION_TANH)
        self._data[1].get_stream_data_indexed(self._out_idx, self._out_data)

        return self._out_data.get_stream_data()
