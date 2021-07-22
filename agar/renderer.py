import pygame as game
from agar import Agar
from vectors import Vector
from debug import Debug
from color import Color
from color import Palette

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
        background_color = Color.as_hex(self.color_gradient[0])
        self.background.fill(game.Color(background_color))

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

    def set_focus(self, agar : Agar = None) -> None:
        self.focus = agar
        return None

    # TODO: Fix grid rendering
    def render_frame(self) -> bool:
        if (self.focus == None):
            origin = Vector()
        else:
            origin = (self.focus.position * -1) + self.center
        for event in game.event.get():
             if event.type == game.QUIT:
                 self.simulation.end()
                 return False
        self.window.blit(self.background, (0, 0))
        # draw the blobs first
        for blob in self.simulation.blobs:
            blob.rect = self.render_agar(blob, origin)
        for agar in self.simulation.agars:
            agar.rect = self.render_agar(agar, origin)
            if (agar.grid != None):
                print("hello")
                self.render_grid(agar.grid)
             # change this to display whatever info we want
             # e.g. agar's id, size, number of eaten things, speed, current position etc
            self.add_text(agar, str(agar.id))
            # 
        game.display.update()
        return True

    def render_grid(self, grid): 
        # game.draw.rect(surface = self.window, color = self.color_gradient[2],  rect = [500, 600, 700, 800], )
        for row in grid:
            for box in row:
                game.draw.rect(surface = self.window, color = self.color_gradient[2],  rect = box, )
                # game.draw.circle(surface = self.window, color = self.color_gradient[2], center = box.center, radius = 100)
            #grid.append(row)
        return None

    # draw a new agar
    def render_agar(self, agar : Agar, origin : Vector = Vector()) -> game.Rect:
        pos = agar.position + origin
        rad = agar.size
        inner_color = game.Color(agar.color_gradient[0])
        color = game.Color(agar.color_gradient[1])
        outline_color = game.Color(agar.color_gradient[2])
        # outline
        outline = game.draw.circle(surface = self.window, color = outline_color, center = (pos.x, pos.y), radius = rad + 3, width = 3)
        # main_circle
        main_circle = game.draw.circle(surface = self.window, color = color, center = (pos.x, pos.y), radius = rad)
        # inner circle
        inner_circle = game.draw.circle(surface = self.window, color = inner_color, center = (pos.x, pos.y), radius = rad * 0.5)
        return main_circle

    def add_text(self, agar : Agar, text : str) -> None:
        color = Color.as_hex(self.color_gradient[2])
        text_surface, text_rect  = self.get_text_object(text, game.Color(color))
        text_rect.center=agar.rect.center
        self.window.blit(text_surface, text_rect)
        return None

    def get_text_object(self, text : str, color : str) -> tuple:
        text_surface = self.font.render(text, True, game.Color(color))
        return (text_surface, text_surface.get_rect())

