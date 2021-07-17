
class Hex():
    def __init__(self, 
                 x : int = 0,
                 y : int = 0,
                 piece = None,
                 rect = None
                 ) -> None:

        self.x = x
        self.y = y
        self.piece = piece
        self.rect = rect
        return

    def __add__(self, c):
        return Hex(self.x + c.x, self.y + c.y)

    def __iadd__(self, c):
        self.x += c.x
        self.y += c.y
        return self

    def __str__(self):
        return "Cell {0}, {1}".format(self.x, self.y)

    # gets all the adjacent cells not in the hive
    def empty_adjacent_hexes(self, hive):
        hexes_constructed = self.adjacent_hexes_constructor()
        empty_hexes = []
        for hex_construct in hexes_constructed:
            if self.find_hex_construct_in_hive(hex_construct, hive) == None:
                empty_hexes.append(hex_construct)
        return empty_hexes

    # gets all the adjacent cells in the hive
    def non_empty_adjacent_hexes(self, hive):
        hexes_constructed = self.adjacent_hexes_constructor()
        non_empty_hexes = []
        for hex_construct in hexes_constructed:
            _hex = self.find_hex_construct_in_hive(hex_construct, hive)
            if _hex != None:
                non_empty_hexes.append(_hex)
        return non_empty_hexes

    def find_hex_construct_in_hive(self, hex_construct, hive):
        for hex in hive.hexes:
            if (hex.x == hex_construct.x and hex.y == hex_construct.y):
                return hex
        return None

    # gets the cells adjacent to the this
    def adjacent_hexes_constructor(self):
        hexes = []
        hexes.append(Hex(self.x - 1, self.y))
        hexes.append(Hex(self.x + 1, self.y))
        hexes.append(Hex(self.x, self.y + 1))
        hexes.append(Hex(self.x , self.y - 1))
        if (self.x % 2 == 0):
            y_dir = 1
        else:
            y_dir = -1
        hexes.append(Hex(self.x - 1, self.y + y_dir))
        hexes.append(Hex(self.x + 1, self.y + y_dir))
        return hexes 


