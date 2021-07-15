from debug import Debug
from cell import Cell
from dataclasses import dataclass
import pygame as game

DEFAULT_ID = 0;

class Player():
    def __init__(self, simulation,
                 int_id : int = DEFAULT_ID,
                 starting_pieces : list = [],
                 is_turn : bool = False
                 ) -> None:

        self.int_id = int_id
        self.is_turn = is_turn

        self.pieces_in_hand = []
        self.add_to_hand(starting_pieces)
        Debug.player_hand(self.pieces_in_hand)
        self.pieces_on_board = []

        return

    def on_turn(self) -> None:
        Debug.player(self.id + " starting turn")
        return

    def place_piece(self, piece, x, y):
        self.simulation.hive.add_piece(piece, x, y)
        return

    def add_to_hand(self, hand : list = None) -> list:
        for piece_class, num in hand:
            for i in range(num):
                piece = piece_class(player = self, int_id = i)
                self.pieces_in_hand.append(piece)
        return

    # conversion that outputs the id
    @property
    def id(self):
        return type(self).__name__ + str(self.int_id)

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
    player : Player = None
    int_id : int = 0
    cell : Cell = Cell()
    _color : tuple = (0, 0, 0)
    rect : game.Rect = None

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
