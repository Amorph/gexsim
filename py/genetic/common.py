
class DNA:
    A = 0
    T = 1
    C = 2
    G = 3


class DNASequences:
    NEURON_CREATE_LAYER = (DNA.C, DNA.A)
    NEURON_CREATE = (DNA.C, DNA.C)
    NEURON_CREATE_LINK = (DNA.C, DNA.T)


# CA - Create layer - invalid if current layer is empty

# CC - Create Neuron
# Neuron properties:
# AA - bias:
#   - (float) bias value (by default 0)
# CT - Create neuron link:
#   - (float) layer index ( 0 - previous layer, -1 - current layer/0 )
#   - (float) target neuron index from 0..1
#   - (float) link weight
