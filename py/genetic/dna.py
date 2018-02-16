from genetic.common import DNA


class DNASequence(bytearray):
    def __init__(self):
        super(DNASequence, self).__init__()
        self.caret = 0

    @property
    def finish(self):
        return self.caret == len(self)

    def read(self):
        self.caret += 1
        return self.__getitem__(self.caret - 1)

    def any(self, *args):
        match = args
        size = 0
        while len(match):
            new_match = []
            if self.caret + size >= len(self):
                break
            b = self.__getitem__(self.caret + size)
            for sequence in match:
                if sequence[size] == b:
                    if len(sequence) == size + 1:
                        self.caret += size + 1
                        return sequence
                    new_match.append(sequence)

            size += 1
            match = new_match
        # if didn't find the match shift to the next
        self.caret += 1
        return None

    def tostring(self):
        result = ""
        for i in range(len(self)):
            val = self.__getitem__(i)
            if val == DNA.A:
                result += "A"
            elif val == DNA.T:
                result += "T"
            elif val == DNA.C:
                result += "C"
            elif val == DNA.G:
                result += "G"
            else:
                result += "<ERROR>"
        return result

    def fromstring(self, str):
        del self[:]
        for char in str:
            if char == 'A':
                self.append(DNA.A)
            elif char == 'T':
                self.append(DNA.T)
            elif char == 'C':
                self.append(DNA.C)
            elif char == 'G':
                self.append(DNA.G)
            else:
                assert not "Wrong character in the string sequence"

        self.caret = 0
