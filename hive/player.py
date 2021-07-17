from hive import Hive
from hive import Rules
from cell import Hex
from piece import Piece
from piece import Queen
from piece import Spider
from piece import Beetle
from piece import Grasshopper
from piece import Ant
from debug import Debug
from color import Palette
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

        add_successful = self.decide_to_add()
        if (add_successful):
            Debug.player(self.id + " added a piece")
            return

        self.decide_to_move()
        
        return

    def decide_to_add(self) -> bool:
        # handled in extensions
        return False

    def decide_to_move(self) -> bool:
        # handled in extensions
        return False

    def try_add_piece_to_hive(self, piece, hex) -> bool:
        Debug.player(self.id + " trying to add piece " + piece.short_id + " to " + str(hex))

        if (Rules.is_valid_add(piece, hex, self.simulation.hive) == False): 
            return False
        
        hex.piece = piece
        self.pieces_on_board.append(piece)
        self.pieces_in_hand.remove(piece)
        self.simulation.hive.hexes.append(hex) 
        
        return True

    def try_move_piece_to_hex(self, piece, cell) -> bool:
        if (Rules.is_valid_move(piece, cell, self)):
            cell.piece = piece
            if (cell not in self.hexes):
                self.hexes.append(cell)
            return True
        return False

    def add_to_hand(self, hand : list = None) -> list:
        for piece_class, num in hand:
            for i in range(num):
                piece = piece_class(int_id = i, player = self)
                self.pieces_in_hand.append(piece)
        return

    # conversion that outputs the id
    @property
    def id(self):
        return type(self).__name__ + str(self.int_id)

    @property
    def color(self):
        return Palette.GREY.SHADES[(self.int_id + 2) % (len(Palette.GREY.SHADES))]

class DumbBot(Player):

    def decide_to_add(self) -> bool:

        add_success = False
        piece, empty_cell = self.random_decision()
        if (piece != None and empty_cell != None):
            add_success = self.try_add_piece_to_hive(piece, empty_cell)

        return add_success

    def random_decision(self):
        hive_hexes = self.simulation.hive.hexes

        # if the hive is empty, add the first hex
        if (len(hive_hexes) == 0):
            empty_hex = Hex()
        else:
            # pick a cell on the hive
            hex = hive_hexes[random.randint(0, len(hive_hexes) - 1)]
            # pick an empty cell next to it
            empty_hexes = hex.empty_adjacent_hexes(self.simulation.hive)
            if (len(empty_hexes) == 0): 
                return (None, None)
            empty_hex = empty_hexes[random.randint(0, len(empty_hexes) - 1)]

        # pick a random piece from the add_to_hand
        if (len(self.pieces_in_hand) == 0): 
            return (None, None)
        piece = self.pieces_in_hand[random.randint(0, len(self.pieces_in_hand) - 1)]

        return (piece, empty_hex)

    def place_piece_near_my_pieces_decision(self):
        
        hive_hexes = self.simulation.hive.hexes
        # if the hive is empty, add the first hex
        if (len(hive_hexes) < 2):
            return self.random_decision()
        else:
            # pick one of your own pieces on the hive
            piece_in_hive = self.pieces_on_board[random.randint(0, len(self.pieces_on_board) - 1)]
            # get the hex its on
            hex = self.simulation.hive.find_piece_in_hive(piece_in_hive)
            # pick an empty cell next to it
            empty_hexes = hex.empty_adjacent_hexes(self.simulation.hive)
            if (len(empty_hexes) == 0): 
                return (None, None)
            empty_hex = empty_hexes[random.randint(0, len(empty_hexes) - 1)]

        # pick a random piece from the add_to_hand
        if (len(self.pieces_in_hand) == 0): 
            return (None, None)
        piece = self.pieces_in_hand[random.randint(0, len(self.pieces_in_hand) - 1)]

        return (piece, empty_hex)

