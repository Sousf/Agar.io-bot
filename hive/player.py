from hive import Hive
from hive import Piece
from hive import Queen
from hive import Spider
from hive import Beetle
from hive import Grasshopper
from hive import Ant
from debug import Debug
import random

DEFAULT_ID = 0;

class Player():
    def __init__(self, simulation,
                 int_id : int = DEFAULT_ID,
                 starting_pieces : list = [],
                 is_turn : bool = False
                 ) -> None:

        self.simulation = simulation
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

    def add_to_hive(self, piece, cell) -> bool:
        if (piece not in self.pieces_in_hand): return False
        self.simulation.hive.add_piece_to_cell(piece, cell)
        self.pieces_in_hand.remove(piece)
        return True

    def add_to_hand(self, hand : list = None) -> list:
        for piece_class, num in hand:
            for i in range(num + 1):
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
        # pick a cell on the hive
        all_cells = self.simulation.hive.cells
        index = random.randint(0, len(all_cells) - 1)
        cell = self.simulation.hive.cells[index]

        # pick an empty cell next to it
        option_cells = cell.empty_adjacent_cells(self.simulation.hive)
        if (len(option_cells) == 0): return
        index_2 = random.randint(0, len(option_cells) - 1)

        # pick a random piece from the add_to_hand
        if (len(self.pieces_in_hand) == 0): return
        index_3 = random.randint(0, len(self.pieces_in_hand) - 1)

        self.add_to_hive(self.pieces_in_hand[index_3], option_cells[index_2])
        return

