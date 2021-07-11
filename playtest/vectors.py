### LIBRARIES ###
import random;
import math;

# Standard vector stuff, with a few useful methods for this particular project
class Vector():
    def __init__(self, x : float = 0, y : float = 0):
        self.x = x;
        self.y = y;
        return;

    # returns the addition of this vector and the passed vector
    def add(self, v): # : Vector = Vector(0, 0)
        return Vector(self.x + v.x, self.y + v.y);

    # adds the passed vector to this vector
    def _add(self, v): # : Vector = Vector(0, 0)
        self.x = self.x + v.x, 
        self.y = self.y + v.y;
        return;

    # returns the scalar product of this vector and the passed scalar
    def scale(self, scalar : float = 0):
        return Vector(self.x * scalar, self.y * scalar);

    # scales this vector by the scalar
    def _scale(self, scalar : float = 0):
        self.x = self.x * scalar, 
        self.y = self.y * scalar;
        return;

    # generates a random direction, normalized to the unit circle
    def randomPosOnUnitCircle():
        x = random.random() - 0.5;
        y = random.random() - 0.5;
        _x = x / math.sqrt(x * x + y * y);
        _y = y / math.sqrt(x * x + y * y);
        return Vector(_x, _y);

    # normalizes a vector
    # i really don't know why i didn't call this normalize
    def mapPosOnUnitCircle(self):
        x = self.x;
        y = self.y;
        _x = x / math.sqrt(x * x + y * y);
        _y = y / math.sqrt(x * x + y * y);
        return Vector(_x, _y);

    # generates a random point within the bounds x,y within (-a,a),(-b,b)
    def withinBounds(a, b):
        x = (random.random() - 0.5) * 2 * a;
        y = (random.random() - 0.5) * 2 * b;
        return Vector(x, y);

    # standard magnitude of this vector
    def magnitude(self):
        x = self.x;
        y = self.y;
        return math.sqrt(x*x + y*y);

    # distance between two given vectors
    def distance(v1, v2):
        x = v1.x - v2.x;
        y = v1.y - v2.y;
        return math.sqrt(x*x + y*y);

