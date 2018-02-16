from math import sqrt


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, tuple) and len(x) >= 3:
            self.x, self.y, self.z = x[0], x[1], x[2]
        else:
            self.x, self.y, self.z = x, y, z

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x,
                           self.y + other.y,
                           self.z + other.z)
        if isinstance(other, float):
            return Vector3(self.x + other,
                           self.y + other,
                           self.z + other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __iadd__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self
        elif isinstance(other, float):
            self.x += other
            self.y += other
            self.z += other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, float):
            return Vector3(self.x - other, self.y - other, self.z - other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __isub__(self, other):
        if isinstance(other, Vector3):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            return self
        elif isinstance(other, float):
            self.x -= other
            self.y -= other
            self.z -= other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def __div__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        if isinstance(other, float):
            return Vector3(self.x / other, self.y / other, self.z / other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __idiv__(self, other):
        if isinstance(other, Vector3):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
            return self
        elif isinstance(other, float):
            self.x /= other
            self.y /= other
            self.z /= other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        if isinstance(other, float):
            return Vector3(self.x * other, self.y * other, self.z * other)
        raise TypeError("Wrong type:" + str(type(other)))

    def __imul__(self, other):
        if isinstance(other, Vector3):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
            return self
        elif isinstance(other, float):
            self.x *= other
            self.y *= other
            self.z *= other
            return self
        raise TypeError("Wrong type:" + str(type(other)))

    def dot(self, vec3) -> float:
        return (self.x * vec3.x +
                self.y * vec3.y +
                self.z * vec3.z)

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
        self.z /= length

        def __repr__(self) -> str:
            return "Vector3({},{},{})".format(self.x, self.y, self.z)
