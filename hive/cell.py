from dataclasses import dataclass

@dataclass
class Cell():

    x : int = 0
    y : int = 0

    def __add__(self, c):
        return Cell(self.x + c.x, self.y + c.y)

    def __iadd__(self, c):
        self.x += c.x
        self.y += c.y
        return self

