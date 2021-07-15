from player import Player
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

                 
