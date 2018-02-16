from math import sqrt


class Vector2:
    ZERO = None # Vector2(0, 0)
    ONE = None # Vector2(1, 1)

    def __init__(self, x: float=0.0, y: float=0.0):
            self.x, self.y = x, y

    def __eq__(self, other):
        if isinstance(other, Vector2):
            return other.x == self.x and other.y == self.y
        return False

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x,
                           self.y + other.y)
        if isinstance(other, float):
            return Vector2(self.x + other,
                           self.y + other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
            return self
        elif isinstance(other, float):
            self.x += other
            self.y += other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x,
                           self.y - other.y)
        if isinstance(other, float):
            return Vector2(self.x - other,
                           self.y - other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __isub__(self, other):
        if isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
            return self
        elif isinstance(other, float):
            self.x -= other
            self.y -= other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def __div__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x,
                           self.y / other.y)
        if isinstance(other, float):
            return Vector2(self.x / other,
                           self.y / other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __idiv__(self, other):
        if isinstance(other, Vector2):
            self.x /= other.x
            self.y /= other.y
            return self
        elif isinstance(other, float):
            self.x /= other
            self.y /= other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x,
                           self.y * other.y)
        if isinstance(other, float):
            return Vector2(self.x * other,
                           self.y * other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __imul__(self, other):
        if isinstance(other, Vector2):
            self.x *= other.x
            self.y *= other.y
            return self
        if isinstance(other, float):
            self.x *= other
            self.y *= other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def dot(self, vec2: 'Vector2') -> float:
        return (self.x * vec2.x +
                self.y * vec2.y)

    @property
    def length(self) -> float:
        return sqrt(self.length_sq)

    @property
    def length_sq(self) -> float:
        return self.dot(self)

    def normalize(self):
        length = self.length
        self.x /= length
        self.y /= length

    def clamp(self, min:'Vector2', max:'Vector2'):
        self.x = min.x if self.x < min.x else self.x
        self.y = min.y if self.y < min.y else self.y

        self.x = max.x if self.x > max.x else self.x
        self.y = max.y if self.y > max.y else self.y

    def __repr__(self) -> str:
        return "Vector2({},{})".format(self.x, self.y)

Vector2.ZERO = Vector2(0, 0)
Vector2.ONE = Vector2(1, 1)