""" LIBRARIES """
import math
import random
import tkinter as gui
import pygame as game
from threading import Timer

""" LOCAL MODULES """
from agar import Agar
from agar import Player
from agar import DumbBot
from agar import Blob
from vectors import Vector
from grid import Grid
from debug import Debug

""" MAGIC VARIABLES """
# default values for simulation (if not specified on initialization)
DEFAULT_NUM_AGARS = 15
DEFAULT_NUM_BLOBS = 50
DEFAULT_BLOB_SPAWN_RATE = 1
DEFAULT_FRAME_RATE = 1/60
DEFAULT_RUN_TIME = 15
# we'll probably want to distinguish between arena boundaries and window boundaries eventually
DEFAULT_WINDOW_HEIGHT = 1080
DEFAULT_WINDOW_WIDTH = 1920

""" BASE SIMULATOR """
class Simulation():
    """
    Runs a simulation for the duration of the run time (note, the run time is calculated on the agar's physics 
    (i.e. it matches the timing that agar's update at so that the simulation completes, 
    regardless of if this matches real time values)
    """
    def __init__(self, num_agars : int = DEFAULT_NUM_AGARS, 
                 num_blobs : int = DEFAULT_NUM_BLOBS, 
                 blob_spawn_rate : float = DEFAULT_BLOB_SPAWN_RATE,
                 height : float = DEFAULT_WINDOW_HEIGHT, 
                 width : float = DEFAULT_WINDOW_WIDTH,
                 frame_rate : float = DEFAULT_FRAME_RATE, 
                 run_time : float = DEFAULT_RUN_TIME):

        Debug.simulation(self.caption)

        # sets the base parameters
        self.num_agars = num_agars
        self.num_agars = num_blobs
        self.blob_spawn_rate = blob_spawn_rate
        self.frame_rate = frame_rate
        self.frames = 0
        self.run_time = run_time
        self.is_running = True

        # used for collisions
        # self.grid = Grid(0, width, height, 10)

        # constructs the interface
        self.renderer = Renderer(self)
        
        # spawns the agars to be used in the simulation
        self.agars = []
        self.spawn_agars(self.num_agars)
        Debug.simulation("Spawned {0} agars".format(len(self.agars)))
        
        # spawns the initial set of blobs, and then starts spawning blobs every so often
        self.blobs = []
        self.spawn_blobs(self.num_agars)
        Debug.simulation("Spawned {0} blobs".format(len(self.blobs)))

        # begins the simulation
        self.start()
        return
    
    """ SPAWNERS """
    # spawns the agars to be used in the simulation
    def spawn_agars(self, num_agars : int = 1) -> None:
        # itterates through the number of agars to be spawned
        for i in range(num_agars):
            # picks out a position to spawn the agar at
            spawn_pos = Vector.random_vector_within_bounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]))
            # constructs the agar object
            agar = Agar(self, id = i, position = spawn_pos, velocity = Vector(), think = True)
            # appends it to the list of agars in the simulation
            self.agars.append(agar)     
        return None 

    # spawns the blobs used in the simulation, defaults to one blob
    def spawn_blobs(self, num_blobs : int = 1) -> None:
        # don't spawn more blobs if the simulation has ended
        if (self.is_running == False): return

        # itterates through the number of blobs to be spawned
        for i in range(num_blobs):
            # picks out a position to spawn the agar at
            spawn_pos = Vector.random_vector_within_bounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]))
            # constructs the blob object
            blob = Blob(self, id = i, position = spawn_pos)
            # appends it to the list of bobs in the simulation
            self.blobs.append(blob)

        # starts a call back for a blob to be spawned at regular intervals
        next_blob_spawn = Timer(self.blob_spawn_rate, self.spawn_blobs, args=None, kwargs=None)
        next_blob_spawn.start()
        return None

    """ CONTROLS """
    # start the simulation
    def start(self):
        Debug.simulation("Starting rendering")
        self.renderer.start()

        # begins the simulation
        next_update = Timer(2, self.update, args=None, kwargs=None)
        next_update.start()
        return

    # shut down the simulation
    def end(self):
        Debug.simulation("Ending rendering")
        for agar in self.agars:
            agar.disable()
        self.agars = []
        self.is_running = False

        # closes the window after a short buffer (not working)
        close_renderer = Timer(3, self.renderer.close, args=None, kwargs=None)
        close_renderer.start()
        return

    # the title of the simulation
    @property
    def caption(self) -> str:
        return "Basic Simulation"

    """ UPDATES """
    # draws a frame on the interface
    def update(self) -> None:
        Debug.simulation("Updating simulation")
        # ends the simulation if it has updated the necessary amount of times
        self.frames += 1
        if (self.frames * self.frame_rate > self.run_time):
            self.end()
            return

        # set the positions
        self.update_positions()
        # set the sizes
        self.update_sizes()
        # update the window
        self.renderer.update()
        # check for collisions
        self.check_collisions()

        Debug.simulation("{0} agars left, and {0} blobs".format(len(self.agars), len(self.blobs)))

        # start a callback to update the next frame at the desired frame rate
        next_update = Timer(self.frame_rate, self.update, args=None, kwargs=None)
        next_update.start()
        return None

    # set the agar positions
    def update_positions(self) -> None:
        for agar in self.agars:
            # update its position based on its velocity
            agar.update_position(self.frame_rate)
            # check that it is within bounds
            agar.check_within_bounds(self.renderer.dimensions)
        return None

    # set the sizes
    def update_sizes(self) -> None:
        for agar in self.agars:
            agar.update_size(self.frame_rate)
        return None

    """ COLLISIONS """
    # checks if agars are colliding
    # probs need to optimise this
    def check_collisions(self) -> None:
        # generate a list of the current active colliders
        agar_colliders = self.get_colliders(self.agars)
        blob_colliders = self.get_colliders(self.blobs)

        # check for agars colliding with other agars
        # copy list to be able to modify original
        agars = self.agars
        for agar in agars:
            # check for agars that have been eaten this frame
            # but are still being itterated over
            # as they have not yet been ejected from the list
            if (agar.is_eaten == False):
                self.agars, agar_colliders = self.check_collision(agar, self.agars, agar_colliders)
                self.blobs, blob_colliders = self.check_collision(agar, self.blobs, blob_colliders)                              
        return None
    
    # check collisions between an agar and a list agars/colliders
    def check_collision(self, agar : Agar, agars : list, colliders : list) -> (list, list):
        # returns the indices of the all the collisions found
        collision_indices = agar.rect.collidelistall(colliders)
        for index in collision_indices:
            # check if the collision results in the agar eating
            agar.on_collision(agars[index])
            # if the agar has been eaten
            if (agars[index].is_eaten):
                # remove the agar collider that was eaten
                # from both lists
                del agars[index]
                del colliders[index]
                # we're editing the active collider list here
                # this is going to make the list of collision indices useless
                # as they point to locations within this active collider list
                # breaking here to avoid the issue
                # but this means only one collision that results in eating can be detected per frame
                # im sure there is a more elegant solution
                return (agars, colliders)
        return (agars, colliders)

    # get the colliders from a list of agars
    def get_colliders(self, agars : list) -> list:
        colliders = []
        for agar in agars:
            if (agar.rect != None):
                colliders.append(agar.rect)
        return colliders

class DumbSimulation(Simulation):
    """ Runs a simulation with ~20 'dumb' agar bots """

    # spawns a dumb bot
    def spawn_agars(self, num_agars : int = 1) -> list:
        for i in range(num_agars):
            spawn_pos = Vector.random_vector_within_bounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]))
            agar = DumbBot(self, id = i, position = spawn_pos, velocity = Vector(), think = True)
            self.agars.append(agar)
        return None

    # the title of the simulation 
    @property
    def caption(self) -> str:
        return "Dumb Bots Simulation"

class PlayerSimulation(Simulation):
    """ Runs a player controlled agar simulation """

    # spawns a player
    def spawn_agars(self, numAgars : int = 1) -> list:
        spawn_pos = Vector(self.renderer.dimensions[0] / 2, self.renderer.dimensions[1] / 2)
        agar = Player(self, id = 0, position = spawn_pos, velocity = Vector(), think = True, think_interval = self.frame_rate)
        self.renderer.set_focus(agar)
        self.agars.append(agar)
        return None

    # the title of the simulation 
    @property
    def caption(self) -> str:
        return "Player Simulation"

class PlayerAndBotSimulation(Simulation):
    """ Runs a player controlled agar simulation with a few 'dumb' bots """

    # spawns a player and a buncha bots
    def spawn_agars(self, numAgars : int = 1) -> list:
        spawn_pos = Vector(self.renderer.dimensions[0] / 2, self.renderer.dimensions[1] / 2)
        agar = Player(self, id = 0, size = 200, position = spawn_pos, velocity = Vector(), think = True, think_interval = self.frame_rate)
        self.agars.append(agar)
        for i in range(1, numAgars + 1):
            spawn_pos = Vector.random_vector_within_bounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]))
            agar = DumbBot(self, id = i, position = spawn_pos, velocity = Vector(), think = True)
            self.agars.append(agar)
        return None

    # the title of the simulation 
    @property
    def caption(self) -> str:
        return "Player and Bot Simulation"

""" RENDERING """
class Renderer():
    def __init__(self, simulation : Simulation, caption : str = "Agar IO", width : float = DEFAULT_WINDOW_WIDTH,  height : float = DEFAULT_WINDOW_HEIGHT, color : str = '#000000'):      
        
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
        for agar in self.simulation.agars:
            agar.rect = self.render_agar(agar)
        for blob in self.simulation.blobs:
            blob.rect = self.render_agar(blob)
        game.display.update()
        return

    def update(self):
        if (self.open == False): return
        if (self.focus == None):
            origin = Vector()
        else:
            origin = (self.focus.position * -1) + self.center
        for event in game.event.get():
             if event.type == game.QUIT:
                 self.close()
        self.window.blit(self.background, (0, 0))
        for agar in self.simulation.agars:
            agar.rect = self.render_agar(agar, origin)
             # change this to display whatever info we want
             # e.g. agar's id, size, number of eaten things, speed, current position etc
            self.add_text(agar, str(agar.id))
        for blob in self.simulation.blobs:
            blob.rect = self.render_agar(blob, origin)
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

    # draw a new agar
    def render_agar(self, agar : Agar, origin : Vector = Vector()) -> game.Rect:
        pos = agar.position + origin
        rad = agar.size
        color = game.Color(agar.convert_size_to_color())
        return game.draw.circle(self.window, color, (pos.x, pos.y), rad)

    def add_text(self, agar : Agar, text : str) -> None:
        text_surface, text_rect  = self.get_text_object(text, game.Color("#ffffff"))
        text_rect.center=agar.rect.center
        self.window.blit(text_surface, text_rect)
        return None

    def get_text_object(self, text : str, color : str) -> tuple:
        text_surface = self.font.render(text, True, game.Color(color))
        return (text_surface, text_surface.get_rect())