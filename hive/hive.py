from debug import Debug
from cell import Hex
from piece import Piece
import pygame as game
from vectors import Vector

DEFAULT_CELL_SIZE = 60

class Hive():
    def __init__(self, hexes : list = [], 
                 hex_size : float = DEFAULT_CELL_SIZE,
                 origin : Vector = Vector() 
                 ) -> None:
        self.hexes = hexes
        self.hex_size = hex_size
        self.origin = origin
        return

    def create_cell(self, x, y) -> None:
        self.hexes.append(Hex(x, y));
        return

    def convert_hex_to_position(self, hex : Hex = Hex()) -> Vector:
        v = Vector(hex.x * self.hex_size, -hex.y * self.hex_size) + self.origin
        if (hex.x % 2 == 1):
           v.y =  v.y + (self.hex_size /2)
        return v

    def find_piece_in_hive(self, piece : Piece) -> Hex:
        for hex in self.hexes:
            if (hex.piece == piece):
                return hex
        return None

class Rules():

    def is_valid_add(piece : Piece, hex : Hex, hive : Hive) -> bool:

        # first two moves don't need to care about connecting
        if (len(hive.hexes) < 2): 
            return True
        elif (Rules.is_in_hand(piece.player, piece) == False): 
            return False
        elif (Rules.not_adjacent_to_other_players(piece.player, hex, hive) == False):
            return False
        elif (Rules.adjacent_to_self(piece.player, hex, hive) == False):
             return False

        return True

    def not_adjacent_to_other_players(player, hex, hive):
        non_empty_hexes = hex.non_empty_adjacent_hexes(hive)
        for _hex in non_empty_hexes:
            if (_hex.piece.player != player):
                Debug.hive("Was adjacent to another players piece")
                return False
        return True

    def adjacent_to_self(player, hex, hive):
        non_empty_hexes = hex.non_empty_adjacent_hexes(hive)
        for _hex in non_empty_hexes:
            if (_hex.piece.player == player):
                return True
        Debug.hive("Was not adjacent to a their own piece")
        return False

    def is_valid_move(piece, hex, hive) -> bool:
        return True

    def is_in_hand(player, piece) -> bool:
        return (piece in player.pieces_in_hand)


