from hive import Player
from hive import Queen
from hive import Spider
from hive import Beetle
from hive import Grasshopper
from hive import Ant
from debug import Debug
from threading import Timer

DEFAULT_CAPTION = "Hive"
DEFAULT_NUMBER_OF_PLAYERS = 2
DEFAULT_MAX_TURNS = 50
DEFAULT_STARTING_PIECES = [(Queen, 1), 
                         (Spider, 2),
                         (Beetle, 2),
                         (Grasshopper, 2),
                         (Ant, 2)]


class Simulation():
    def __init__(self, caption : str = DEFAULT_CAPTION,
                 number_of_players : int = DEFAULT_NUMBER_OF_PLAYERS,
                 max_turns : int = DEFAULT_MAX_TURNS,
                 starting_pieces : list = DEFAULT_STARTING_PIECES,
                 ) -> None:
        
        self.caption = caption
        self.turn_number = 0
        self.max_turns = max_turns
        #self.renderer = Renderer(self)

        Debug.simulation("Initializing a " + self.caption + " for {0} turns, with {1} players".format(self.max_turns, number_of_players))

        # create the players
        self.players = []
        self.create_players(number_of_players, starting_pieces)
        
        self.start()

        return

    def create_players(self, number_of_players : int, starting_pieces : list = []) -> None:
        for i in range(number_of_players):
            player = Player(simulation = self, int_id = i, starting_pieces = starting_pieces)
            self.players.append(player)
        return

    def start(self) -> None:
        # can either run a for loop to run MAX_TURNS or do it recursively
        # think the for loop might be better
        #self.renderer.start()
        self.run_turn()
        return

    def run_turn(self) -> None:
        self.turn_number += 1
        if (self.turn_number > self.max_turns): 
            self.end()
            return
        Debug.simulation_update("Running turn number {0}".format(self.turn_number))
        for player in self.players:
            player.on_turn()
        self.run_turn()
        return

    def end(self) -> None:
        # print out scores or some shizz
        Debug.simulation("Ending simulation")
        #close_renderer = Timer(3, self.renderer.close, args=None, kwargs=None)
        #close_renderer.start()
        return

""" RENDERING
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
"""

                 
