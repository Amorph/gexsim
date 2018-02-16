import random

from genetic.common import DNA
from genetic.dna import DNASequence


def mutate(dna: DNASequence, mutation_count: int) -> None:
    while mutation_count:
        mutation_count -= 1
        index = random.randint(0, len(dna)-1)
        shift = random.randint(DNA.A, DNA.G)
        dna.insert(index, shift)
        #dna[index] = (dna[index] + shift) % (DNA.G + 1)
