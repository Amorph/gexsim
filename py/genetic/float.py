from genetic.common import DNA
from genetic.dna import DNASequence

EPS = 0.001

# Float encoding -N....0....N
# A - select first half
# T - select second half
# C -
# - A - select start of range
# - T - select center of range
# - C - select end of range
# - G - increase range by two
# G - invalid

_SELECT_RANGE_START = (DNA.G, DNA.A)
_SELECT_RANGE_CENTER = (DNA.G, DNA.T)
_SELECT_RANGE_END = (DNA.G, DNA.C)

_INCREASE_RANGE = (DNA.G, DNA.G)

_SELECT_FIRST_HALF = (DNA.A, )
_SELECT_SECOND_HALF = (DNA.T, )


def encode(dna: DNASequence, value: float, accuracy: float = EPS):
    r = (-1.0, 0.0, 1.0)
    while True:
        # check for match and range control values
        if abs(r[0] - value) <= accuracy:
            dna.extend(_SELECT_RANGE_START)
            break
        if abs(r[1] - value) <= accuracy:
            dna.extend(_SELECT_RANGE_CENTER)
            break
        if abs(r[2] - value) <= accuracy:
            dna.extend(_SELECT_RANGE_END)
            break

        if value < r[0] or value > r[2]:
            dna.extend(_INCREASE_RANGE)
            r = (r[0]*2, r[1], r[2]*2)
            continue

        if r[0] < value < r[1]:
            dna.extend(_SELECT_FIRST_HALF)
            r = (r[0], r[0] + (r[1] - r[0]) * 0.5, r[1])
            continue

        if r[1] < value < r[2]:
            dna.extend(_SELECT_SECOND_HALF)
            r = (r[1], r[1] + (r[2] - r[1]) * 0.5, r[2])
            continue

        assert False and "Problem"


def decode(dna: DNASequence) -> float:
    r = (-1.0, 0.0, 1.0)
    while not dna.finish:
        c = dna.any(_SELECT_FIRST_HALF, _SELECT_SECOND_HALF, _INCREASE_RANGE,
                    _SELECT_RANGE_START, _SELECT_RANGE_CENTER, _SELECT_RANGE_END)

        if c == _SELECT_FIRST_HALF:
            r = (r[0], r[0] + (r[1] - r[0]) * 0.5, r[1])
            continue
        elif c == _SELECT_SECOND_HALF:
            r = (r[1], r[1] + (r[2] - r[1]) * 0.5, r[2])
            continue
        elif c == _INCREASE_RANGE:
            r = (r[0] * 2, r[1], r[2] * 2)
            continue
        elif c == _SELECT_RANGE_START:
            return r[0]
        elif c == _SELECT_RANGE_CENTER:
            return r[1]
        elif c == _SELECT_RANGE_END:
            return r[2]
        else:
            break
    return r[1]
