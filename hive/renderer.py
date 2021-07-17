import pygame as game
from vectors import Vector
from color import Color
from color import Palette
from debug import Debug
from cell import Hex
from hive import Hive
from piece import Piece

""" RENDERING """
class Renderer():
    def __init__(self, simulation, width : float,  height : float, caption : str = "Agar IO", color_gradient : tuple = None):      
        
        self.simulation = simulation
        self.dimensions = (width, height)
        self.center = Vector(self.dimensions[0] / 2, self.dimensions[1] / 2)
        if (color_gradient == None):
            grey = Palette.GREY
            color_gradient = (grey.lightest_shade, grey.middle_shade, grey.darkest_shade)
        self.color_gradient = color_gradient

        self.caption = self.simulation.caption or caption
        game.display.set_caption(self.caption)
        self.window = game.display.set_mode(self.dimensions)
        self.background = game.Surface(self.dimensions)
        # background_color = Color.as_hex(self.color_gradient[0])
        self.background.fill(game.Color(self.color_gradient[0]))

        self.focus = None
        return

    def start(self):
        game.init()
        self.font = game.font.Font('freesansbold.ttf', 12)
        self.open = True
        self.render_frame()
        return

    def update(self) -> None:
        if (self.open == False): return
        self.render_frame()
        return

    def close(self) -> None:
        game.display.quit()
        game.quit()
        self.open = False
        return None

    def render_frame(self) -> None:      
        for event in game.event.get():
             if event.type == game.QUIT:
                 self.simulation.end()
                 return
        self.window.blit(self.background, (0, 0))
        for hex in self.simulation.hive.hexes:
            hex.rect = self.render_hex(hex)
            # self.add_text(hex, str(hex.piece.short_id))
            for empty_hex in hex.empty_adjacent_hexes(self.simulation.hive):
                self.render_hex(empty_hex)
        game.display.update()
        return

    # draw a new agar
    def render_hex(self, cell : Hex) -> game.Rect:
        if (cell.piece == None): cell.piece = Piece(); # make this an empty piece
        pos = self.simulation.hive.convert_hex_to_position(cell)
        length = self.simulation.hive.hex_size / 2
        color = game.Color(cell.piece.color)
        
        outline_points = pos.regular_polygon_as_tuples(6, length + 3)
        outline_color = game.Color(self.color_gradient[2])
        outline_polygon = game.draw.polygon(self.window, outline_color, outline_points)

        if (cell.piece.player != None):
            factor = 1.5
            player_points = pos.regular_polygon_as_tuples(6, length)
            player_color = game.Color(cell.piece.player.color)
            player_polygon = game.draw.polygon(self.window, player_color, player_points)

        else:
            factor = 1

        polygon_points = pos.regular_polygon_as_tuples(6, length / factor)
        return game.draw.polygon(self.window, color, polygon_points)

    def add_text(self, cell : Hex, text : str) -> None:
        text_surface, text_rect  = self.get_text_object(text, game.Color(self.color_gradient[2]))
        text_rect.center=cell.rect.center
        self.window.blit(text_surface, text_rect)
        return None

    def get_text_object(self, text : str, color : str) -> tuple:
        text_surface = self.font.render(text, True, game.Color(color))
        return (text_surface, text_surface.get_rect())

    
