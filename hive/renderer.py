import pygame as game
from vectors import Vector
from debug import Debug
from cell import Cell
from cell import Hexagon
from hive import Piece
from hive import Hive
from hive import Queen

""" RENDERING """
class Renderer():
    def __init__(self, simulation, width : float,  height : float, caption : str = "Agar IO", color : str = '#000000'):      
        
        self.simulation = simulation
        self.dimensions = (width, height)
        self.center = Vector(self.dimensions[0] / 2, self.dimensions[1] / 2)
        self.color = color

        self.caption = self.simulation.caption or caption
        game.display.set_caption(self.caption)
        self.window = game.display.set_mode(self.dimensions)
        self.background = game.Surface(self.dimensions)
        self.background.fill(game.Color(self.color))

        self.focus = None
        return

    def start(self):
        game.init()
        self.font = game.font.Font('freesansbold.ttf', 15)
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
        for cell in self.simulation.hive.cells:
            if cell.piece != None:
                cell.rect = self.render_cell(cell)
                self.add_text(cell, str(cell.piece.short_id))
                for empty_adj_cell in cell.empty_adjacent_cells(self.simulation.hive):
                     self.render_cell(empty_adj_cell)
        game.display.update()
        return

    # draw a new agar
    def render_cell(self, cell : Cell) -> game.Rect:
        if (cell.piece == None): cell.piece = Piece(); # make this an empty piece
        pos = self.simulation.hive.convert_cell_to_position(cell)
        length = self.simulation.hive.cell_size / 2
        color = game.Color(cell.piece.color)
        polygon_points = pos.regular_polygon_as_tuples(6, length)
        return game.draw.polygon(self.window, color, polygon_points)

    def add_text(self, cell : Cell, text : str) -> None:
        text_surface, text_rect  = self.get_text_object(text, game.Color("#ffffff"))
        text_rect.center=cell.rect.center
        self.window.blit(text_surface, text_rect)
        return None

    def get_text_object(self, text : str, color : str) -> tuple:
        text_surface = self.font.render(text, True, game.Color(color))
        return (text_surface, text_surface.get_rect())

# ---------------- Testing ----------------- #
def _render_frame(hive, window):
    for cell in hive.cells:
        if cell.piece != None:
            _render_cell(cell, hive, window)
            for adj_cell in cell.empty_adjacent_cells(hive):
                _render_cell(adj_cell, hive, window)
    return


def _render_cell(cell, hive, window):
    if (cell.piece == None): cell.piece = Piece();
    pos = hive.convert_cell_to_position(cell)
    length = hive.cell_size / 2
    color = game.Color(cell.piece.color)
    polygon_points = pos.regular_polygon_as_tuples(6, length)
    return game.draw.polygon(window, color, polygon_points)

if __name__ == "__main__":
    game.init()
    game.display.set_caption("Test")
    dimensions = (500, 500)
    window = game.display.set_mode(dimensions)
    background = game.Surface(dimensions)
    background.fill(game.Color("#ffffff"))
    
    cells = [Hexagon(0, 0), Hexagon(1, 0), Hexagon(1, -1), Hexagon(1, 1)]
    """for i in range(-20, 20):
        for j in range(0, 1):
            cells.append(Cell(i, j));"""
    hive = Hive(cells = cells, center = Vector(250, 250))
    for cell in hive.cells:
        piece = Queen()
        cell.piece = piece
    _render_frame(hive, window)
    game.display.update()
    while True:
        for event in game.event.get():
            if event.type == game.QUIT:
                game.display.quit()
                game.quit()   



    
