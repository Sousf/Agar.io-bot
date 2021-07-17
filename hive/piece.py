import pygame as game

from color import Palette

DEFAULT_ID = 0

class Piece():
    # initializion
    _color = Palette.GREY.LAVENDER

    def __init__(self, 
                 int_id : int = DEFAULT_ID,
                 player = None,
                 rect : game.Rect = None,
                 ) -> None:

        self.int_id = int_id
        self.player = player
        self.rect = rect
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

class Queen(Piece):
    # overriden initializion   
    _color = Palette.YELLOW.CRAYOLA

class Spider(Piece):
    # overriden initializion  
    _color = Palette.RED.CHESTNUT

class Beetle(Piece):
    # overriden initializion    
    _color = Palette.BLUE.SKY

class Grasshopper(Piece):
    # overriden initializion
    _color = Palette.GREEN.MARINE

class Ant(Piece):
    # overriden initializion
    _color = Palette.RED.VERMILLION

if __name__ == "__main__":
    piece = Piece()
    print(piece.color)
    queen = Queen()
    print(queen.color)

