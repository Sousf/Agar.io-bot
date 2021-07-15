import pygame as game

""" RENDERING """
class Renderer():
    def __init__(self, simulation : Simulation, caption : str = DEFAULT_CAPTION, width : float = DEFAULT_WINDOW_WIDTH,  height : float = DEFAULT_WINDOW_HEIGHT, color : str = '#000000'):      
        
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


    def render_frame(self) -> None:      
        for event in game.event.get():
             if event.type == game.QUIT:
                 self.simulation.end()
        self.window.blit(self.background, (0, 0))
        for piece in self.simulation.hive:
            piece.rect = self.render_piece(piece, origin)
            # change this to display whatever info we want
            # e.g. agar's id, size, number of eaten things, speed, current position etc
            self.add_text(piece, str(piece.id))
        return

    # draw a new agar
    def render_piece(self, piece : Piece) -> game.Rect:
        pos = self.hive.convert_cell_to_position(piece.cell)
        rad = self.hive.cell_size
        color = piece.Color(piece.color)
        return game.draw.circle(self.window, color, (pos.x, pos.y), rad)

    def add_text(self, piece : Piece, text : str) -> None:
        text_surface, text_rect  = self.get_text_object(text, game.Color("#ffffff"))
        text_rect.center=piece.rect.center
        self.window.blit(text_surface, text_rect)
        return None

    def get_text_object(self, text : str, color : str) -> tuple:
        text_surface = self.font.render(text, True, game.Color(color))
        return (text_surface, text_surface.get_rect())
