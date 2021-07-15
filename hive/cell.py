from dataclasses import dataclass

@dataclass
class Cell():

    x : int = 0
    y : int = 0
    piece = None
    rect = None

    def __add__(self, c):
        return Cell(self.x + c.x, self.y + c.y)

    def __iadd__(self, c):
        self.x += c.x
        self.y += c.y
        return self

    def empty_adjacent_cells(self, hive):
        adj_cells = self.adjacent_cells()
        empty_adj_cells = []
        for adj_cell in adj_cells:
            if (adj_cell not in hive.cells):
                empty_adj_cells.append(adj_cell)
        return empty_adj_cells

    def adjacent_cells(self):
        return


@dataclass
class Hexagon(Cell):

    def adjacent_cells(self):
        adj_cells = []
        adj_cells.append(Hexagon(self.x - 1, self.y))
        adj_cells.append(Hexagon(self.x + 1, self.y))
        adj_cells.append(Hexagon(self.x, self.y + 1))
        adj_cells.append(Hexagon(self.x , self.y - 1))
        if (self.x % 2 == 0):
            y_dir = 1
        else:
            y_dir = -1
        adj_cells.append(Hexagon(self.x - 1, self.y + y_dir))
        adj_cells.append(Hexagon(self.x + 1, self.y + y_dir))
        return adj_cells 
