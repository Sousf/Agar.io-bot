from hive import Hive
from hive import Piece
from hive import Queen
from hive import Spider
from hive import Beetle
from hive import Grasshopper
from hive import Ant
from debug import Debug

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

    def add_to_hive(self, piece, x, y) -> bool:
        if (piece not in self.pieces_in_hand): return False
        self.simulation.hive.add_piece(piece, x, y)
        return True

    def add_to_hand(self, hand : list = None) -> list:
        for piece_class, num in hand:
            for i in range(num):
                piece = piece_class(int_id = i)
                piece.assign_to_player(self)
                self.pieces_in_hand.append(piece)
        return

    # conversion that outputs the id
    @property
    def id(self):
        return type(self).__name__ + str(self.int_id)

class DumbBot(Player):

    def on_turn(self) -> None:
        Debug.player(self.id + " starting turn")
        #if (self.pieces_in_hand != None)
        return

