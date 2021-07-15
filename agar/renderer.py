import pygame as game
from agar import Agar
from vectors import Vector
from debug import Debug

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
        game.display.update()
        return

    def update(self):
        if (self.open == False): return
        self.render_frame()
        game.display.update()
        return

    def close(self) -> None:
        game.display.quit()
        game.quit()
        self.open = False
        return None

    def set_focus(self, agar : Agar = None) -> None:
        self.focus = agar
        return None

    def render_frame(self) -> None:
        if (self.focus == None):
            origin = Vector()
        else:
            origin = (self.focus.position * -1) + self.center
        for event in game.event.get():
             if event.type == game.QUIT:
                 self.simulation.end()
        self.window.blit(self.background, (0, 0))
        for agar in self.simulation.agars:
            agar.rect = self.render_agar(agar, origin)
             # change this to display whatever info we want
             # e.g. agar's id, size, number of eaten things, speed, current position etc
            self.add_text(agar, str(agar.id))
        for blob in self.simulation.blobs:
            blob.rect = self.render_agar(blob, origin)
        return

    # draw a new agar
    def render_agar(self, agar : Agar, origin : Vector = Vector()) -> game.Rect:
        pos = agar.position + origin
        rad = agar.size
        color = game.Color(agar.color)
        return game.draw.circle(self.window, color, (pos.x, pos.y), rad)

    def add_text(self, agar : Agar, text : str) -> None:
        text_surface, text_rect  = self.get_text_object(text, game.Color("#ffffff"))
        text_rect.center=agar.rect.center
        self.window.blit(text_surface, text_rect)
        return None

    def get_text_object(self, text : str, color : str) -> tuple:
        text_surface = self.font.render(text, True, game.Color(color))
        return (text_surface, text_surface.get_rect())

