from debug import Debug
from cell import Cell
from dataclasses import dataclass
import pygame as game

DEFAULT_ID = 0

@dataclass
class Hive():
    # initialization
    cells : list[Cell] = list[Cell()]
    
    def create_cell(self, x, y) -> None:
        self.cells.append(Cell(x, y));
        return


@dataclass
class Piece():
    # initializion
    int_id : int = DEFAULT_ID
    cell : Cell = Cell()
    _color : tuple = (0, 0, 0)
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
        return type(self).__name__ + str(self.int_id)

    def id(self) -> str:
        if (self.player != None):
            return self.player.id + type(self).__name__ + str(self.int_id)
        return type(self).__name__ + str(self.int_id)

@dataclass
class Queen(Piece):
    # overriden initializion   
    _color : tuple = (255, 255, 0)

@dataclass
class Spider(Piece):
    # overriden initializion  
    _color : tuple = (128, 48, 0)

@dataclass
class Beetle(Piece):
    # overriden initializion    
    _color : tuple = (160, 64, 80)

@dataclass
class Grasshopper(Piece):
    # overriden initializion
    _color : tuple = (255, 0, 0)

@dataclass
class Ant(Piece):
    pass

if __name__ == "__main__":
    piece = Piece()
    print(piece.color)
    queen = Queen()
    print(queen.color)
