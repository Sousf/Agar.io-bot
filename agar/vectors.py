### LIBRARIES ###
import random
import math
from dataclasses import dataclass

# Standard vector stuff, with a few useful methods for this particular project
@dataclass
class Vector():

    x : float = 0
    y : float = 0

    # returns the addition of this vector and the passed vector
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y)

    # adds the passed vector to this vector
    def __iadd__(self, v):
        self.x = self.x + v.x 
        self.y = self.y + v.y
        return self

    # returns the subtraction of this vector and the passed vector
    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y)

    # subtracts the passed vector to this vector
    def __isub__(self, v):
        self.x = self.x - v.x 
        self.y = self.y - v.y
        return self

    # returns the scalar product of this vector and the passed scalar
    def __mul__(self, scalar : float = 1):
        return Vector(self.x * scalar, self.y * scalar)

    # scales this vector by the scalar
    def __imul__(self, scalar : float = 1):
        self.x = self.x * scalar, 
        self.y = self.y * scalar
        return self

    # returns the scalar division of this vector and the passed scalar
    def __truediv__(self, scalar : float = 1):
        if (scalar == 0):
            raise ValueError("Cannot divide by 0");
            return self;
        return Vector(self.x / scalar, self.y / scalar)

    # scales this vector by the scalar
    @property
    def as_tuple(self):
        return (self.x, self.y);

    # generates a random direction, normalized to the unit circle
    def random_normalized_vector():
        x = random.random() - 0.5
        y = random.random() - 0.5
        normalized_x = x / math.sqrt(x * x + y * y)
        normalized_y = y / math.sqrt(x * x + y * y)
        return Vector(normalized_x, normalized_y)

    # normalizes a vector
    def normalize(self):
        if (self.x == 0 and self.y == 0): return Vector()
        normalized_x = self.x / self.magnitude()
        normalized_y = self.y / self.magnitude()
        return Vector(normalized_x, normalized_y)

    # generates a random point within the bounds x,y within (a0, a1),(b0, b1)
    def random_vector_within_bounds(horizontal_bounds : tuple = (0, 1), vertical_bounds : tuple = (0, 1)):
        x = random.random() * (horizontal_bounds[1] - horizontal_bounds[0])
        y = random.random() * (vertical_bounds[1] - vertical_bounds[0])
        return Vector(x, y)

    # standard magnitude of this vector
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    # distance between two given vectors
    def distance(v1, v2):
        x = v1.x - v2.x
        y = v1.y - v2.y
        return math.sqrt(x*x + y*y)

    # distance between two given vectors
    def mid_point(self, v1, v2 = None):
        if (v2 == None): v2 = self
        x = (v1.x + v2.x) / 2
        y = (v1.y + v2.y) / 2
        return Vector(x, y)

    # angle in radians
    def rotate(self, angle : float = 0): 
        angle = angle / 180 * math.pi
        x_rotated = round(math.cos(angle) * self.x - math.sin(angle) * self.y, 3)
        y_rotated = round(math.sin(angle) * self.x + math.cos(angle) * self.y, 3)
        return Vector(x_rotated, y_rotated)

    def regular_polygon(self, points : int = 0, length : float = 1) -> list:
        vectors = []
        for i in range(points):
            angle = 360 * i / points
            vectors.append(self + Vector(length, 0).rotate(angle))
        return vectors

    def regular_polygon_as_tuples(self, points : int = 0, length : float = 1) -> list:
        _points = []
        for i in range(points):
            angle = 360 * i / points
            _points.append((self + Vector(length, 0).rotate(angle)).as_tuple)
        return _points
    
    def shake(self, max_angle : float = 0):
        random_angle = 2 * (random.random() - 0.5) * max_angle
        return self.rotate(random_angle)



