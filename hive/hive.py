from debug import Debug
from cell import Cell
from cell import Hexagon
from dataclasses import dataclass
import pygame as game
from vectors import Vector

DEFAULT_ID = 0
DEFAULT_CELL_SIZE = 60

@dataclass
class Hive():
    def __init__(self, cells : list = [Hexagon()], 
                 cell_size : float = DEFAULT_CELL_SIZE,
                 center : Vector = Vector() 
                 ) -> None:
        self.cells = cells
        self.cell_size = cell_size
        self.center = center
        return

    def create_cell(self, x, y) -> None:
        self.cells.append(Cell(x, y));
        return

    def convert_cell_to_position(self, cell : Cell = Cell()) -> Vector:
        v = Vector(cell.x * self.cell_size, -cell.y * self.cell_size) + self.center
        if (cell.x % 2 == 1):
           v.y =  v.y + (self.cell_size /2)
        #if (cell.x != 0):
            #v = v.rotate(cell.y * 360 / (6 * cell.x))
            #pass
        return v

    def add_piece_to_cell(self, piece, cell):
        cell.piece = piece
        self.cells.append(cell)
        return


@dataclass
class Piece():
    # initializion
    int_id : int = DEFAULT_ID
    _color : tuple = (64, 64, 64)
    rect : game.Rect = None
    player = None

    def assign_to_player(self, player):
        self.player = player
        return

    @property
    def color(self) -> str:
        return '#%02x%02x%02x' % self._color

    @property
    def short_id(self) -> str:
        if (self.player != None):
            return str(self.player.int_id) + type(self).__name__ + str(self.int_id)
        return type(self).__name__ + str(self.int_id)

    def id(self) -> str:
        if (self.player != None):
            return self.player.id + type(self).__name__ + str(self.int_id)
        return type(self).__name__ + str(self.int_id)

@dataclass
class Queen(Piece):
    # overriden initializion   
    _color : tuple = (128, 128, 0)

@dataclass
class Spider(Piece):
    # overriden initializion  
    _color : tuple = (128, 0, 128)

@dataclass
class Beetle(Piece):
    # overriden initializion    
    _color : tuple = (0, 128, 0)

@dataclass
class Grasshopper(Piece):
    # overriden initializion
    _color : tuple = (0, 0, 128)

@dataclass
class Ant(Piece):
    # overriden initializion
    _color : tuple = (128, 0, 0)
    pass

if __name__ == "__main__":
    piece = Piece()
    print(piece.color)
    queen = Queen()
    print(queen.color)
