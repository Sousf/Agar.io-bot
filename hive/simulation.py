from player import Player
from player import DumbBot

from hive import Hive
from hive import Queen
from hive import Spider
from hive import Beetle
from hive import Grasshopper
from hive import Ant
from debug import Debug
from threading import Timer
from renderer import Renderer
from vectors import Vector

DEFAULT_CAPTION = "Hive"
DEFAULT_NUMBER_OF_PLAYERS = 2
DEFAULT_MAX_TURNS = 50
DEFAULT_STARTING_PIECES = [(Queen, 1), 
                           (Spider, 2),
                           (Beetle, 2),
                           (Grasshopper, 2),
                           (Ant, 2)]
# we'll probably want to distinguish between arena boundaries and window boundaries eventually
DEFAULT_WINDOW_HEIGHT = int(1080 / 1.5)
DEFAULT_WINDOW_WIDTH = int(1920 / 2)


class Simulation():
    def __init__(self, caption : str = DEFAULT_CAPTION,
                 number_of_players : int = DEFAULT_NUMBER_OF_PLAYERS,
                 max_turns : int = DEFAULT_MAX_TURNS,
                 starting_pieces : list = DEFAULT_STARTING_PIECES,
                 height : float = DEFAULT_WINDOW_HEIGHT, 
                 width : float = DEFAULT_WINDOW_WIDTH,
                 ) -> None:
        
        self.caption = caption
        self.turn_number = 0
        self.max_turns = max_turns
        self.is_running = True

        self.hive = Hive(center = Vector(width / 2, height / 2))
        self.renderer = Renderer(self, width = width, height = height)

        Debug.simulation("Initializing a " + self.caption + " for {0} turns, with {1} players".format(self.max_turns, number_of_players))

        # create the players
        self.players = []
        self.create_players(number_of_players, starting_pieces)
        
        self.start()
        self.next_turn = None
        self.delayed_end = None

        return

    def create_players(self, number_of_players : int, starting_pieces : list = []) -> None:
        for i in range(number_of_players):
            player = DumbBot(simulation = self, int_id = i, starting_pieces = starting_pieces)
            self.players.append(player)
        return

    def start(self) -> None:
        # can either run a for loop to run MAX_TURNS or do it recursively
        # think the for loop might be better
        self.renderer.start()
        self.next_turn = Timer(2, self.run_turn, args=None, kwargs=None)
        self.next_turn.start()
        return

    def run_turn(self) -> None:
        self.turn_number += 1

        # ends the simulation if something external has caused it to stop running
        if (self.is_running == False): return
        # or ends the simulation if it has run its course
        elif (self.turn_number > self.max_turns): 
            self.delayed_end = Timer(3, self.end, args=None, kwargs=None)
            self.delayed_end.start()
            return

        Debug.simulation_update("Running turn number {0}".format(self.turn_number))
        for player in self.players:
            player.on_turn()

        self.renderer.update()
        
        self.next_turn = Timer(0.25, self.run_turn, args=None, kwargs=None)
        self.next_turn.start()
        return

    # shut down the simulation
    def end(self):
        Debug.simulation("Ending rendering")
        self.is_running = False

        # fail safe for force quitting in between simulation end and renderer closing
        if (self.delayed_end != None and self.delayed_end.is_alive()): self.delayed_end.cancel()
        # cancels the next update if the simulation has not completed
        if (self.next_turn != None and self.next_turn.is_alive()): self.next_turn.cancel()

        # closes the window after a short buffer (not working)
        self.renderer.close()
        return

                 
