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

        # back propagation data
        self._bp_error = G.create_stream(self._data[0].type, self._data[0].count)
        self._bp_delta = G.create_stream(self._bp_error.type, self._bp_error.count)
        self._bp_links = G.create_stream(self._links.type, self._links.count)
        self.__build_bp_links(self._links)

        self._bp_delta.clear()
        self._bp_error.clear()

    def __build_bp_links(self, forward_links):
        lock_x = forward_links.lock(0, 0, 0)
        lock_y = self._bp_links.lock(0, 0, 0)
        lock_y.data = [(y, x) for x, y in lock_x.data]
        lock_x.unlock(), lock_y.unlock()

    def process(self, inputs):
        assert len(inputs) == self._in_data.count

        self._in_data.set_stream_data(inputs)
        self._data[1].set_stream_data_indexed(self._in_idx, self._in_data)

        self._data[0].copy(self._biases)
        self._data[0].multiply_add_links(self._links, self._data[1], self._weights)
        self._data[1].process_stream(self._data[0], GN.GN_FUNCTION_TANH)
        self._data[1].get_stream_data_indexed(self._out_idx, self._out_data)

        return self._out_data.get_stream_data()

    def back_propagate(self, learning_rate, outputs):
        assert len(outputs) == self._out_data.count

        # temp realization in python
        self._bp_error.clear()

        lock_data = self._data[0].lock(0, 0, 0)

        # calculate error on all links
        self._bp_error.multiply_add_links(self._bp_links, self._bp_delta, self._weights)

        # put expected value error
        lock_error = self._bp_error.lock(0, 0, 0)
        lock_out_idx = self._out_idx.lock(0, 0, 0)
        for i, expected in enumerate(outputs):
            data_i = lock_out_idx.data[i]
            lock_error.data[data_i] = expected - lock_data.data[data_i]
        lock_out_idx.unlock(), lock_error.unlock()

        # update back propagation weight delta
        lock_error = self._bp_error.lock(0, 0, 0)
        lock_delta = self._bp_delta.lock(0, 0, 0)
        for i in range(lock_delta.count):
            data = lock_data.data[i]
            lock_delta.data[i] = lock_error.data[i] * (data * (1.0 - data))

        lock_delta.unlock()
        lock_data.unlock()

        # update weights
        lock_weights = self._weights.lock(0, 0, 0)
        lock_links = self._links.lock(0, 0, 0)
        lock_data = self._data[1].lock(0, 0, 0)
        lock_delta = self._bp_delta.lock(0, 0, 0)

        for i in range(lock_links.count):
            link_i, link_o = lock_links.data[i]
            lock_weights.data[link_o] += learning_rate * lock_delta.data[link_o] * lock_data.data[link_i]

        lock_weights.unlock(), lock_links.unlock(), lock_data.unlock()
        lock_delta.unlock()

        # update biases
        lock_bias = self._bp_delta.lock(0, 0, 0)
        lock_delta = self._bp_delta.lock(0, 0, 0)
        for i in range(lock_bias.count):
            lock_bias.data[i] += learning_rate * lock_delta.data[i]

        lock_bias.unlock(), lock_delta.unlock()
