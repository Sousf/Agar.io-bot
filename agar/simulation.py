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
from renderer import Renderer

""" MAGIC VARIABLES """
# default values for simulation (if not specified on initialization)
DEFAULT_NUM_AGARS = 15
DEFAULT_NUM_BLOBS = 50
DEFAULT_BLOB_SPAWN_RATE = 1 # blobs per second
DEFAULT_FRAME_RATE = 1/60
DEFAULT_RUN_TIME = 15
# we'll probably want to distinguish between arena boundaries and window boundaries eventually
DEFAULT_WINDOW_HEIGHT = int(1080 / 1.5)
DEFAULT_WINDOW_WIDTH = int(1920 / 2)

""" BASE SIMULATOR """
class Simulation():
    """
    Runs a simulation for the duration of the run time (note, the run time is calculated on the agar's physics 
    (i.e. it matches the timing that agar's update at so that the simulation completes, 
    regardless of if this matches real time values)
    """
    def __init__(self, caption : str = "Base Simulation",
                 player : bool = False,
                 num_bots : int = DEFAULT_NUM_AGARS, 
                 num_blobs : int = DEFAULT_NUM_BLOBS, 
                 blob_spawn_rate : float = DEFAULT_BLOB_SPAWN_RATE,
                 height : float = DEFAULT_WINDOW_HEIGHT, 
                 width : float = DEFAULT_WINDOW_WIDTH,
                 frame_rate : float = DEFAULT_FRAME_RATE, 
                 run_time : float = DEFAULT_RUN_TIME
                 ):

        self.caption = caption;

        # sets the base parameters
        self.player_is_active = player
        self.num_bots = num_bots
        self.num_blobs = num_blobs
        self.blob_spawn_rate = blob_spawn_rate
        self.blob_spawn_timer = 0
        self.frame_rate = frame_rate
        self.frames = 0
        self.frame_callbacks = {}
        self.run_time = run_time
        self.is_running = True

        # used for collisions
        # self.grid = Grid(0, width, height, 10)

        Debug.simulation("Running " + self.caption + " for {0} seconds at {1:.2f} frames per second".format(self.run_time, (1 / self.frame_rate)))
        # constructs the interface
        self.renderer = Renderer(self, width = width, height = height)

        # spawn the player if necessary
        self.agars = []
        if (player): self.spawn_player()
        Debug.simulation("Spawned a player")
        
        # spawns the agars to be used in the simulation
        self.spawn_bots(self.num_bots)
        Debug.simulation("Spawned {0} agars".format(len(self.agars)))
        
        # spawns the initial set of blobs, and then starts spawning blobs every so often
        self.blobs = []
        self.spawn_blobs(self.num_blobs)
        Debug.simulation("Spawned {0} blobs".format(len(self.blobs)))

        # begins the simulation
        self.start()
        return
    
    """ SPAWNERS """
    # spawns the player to be used in the simulation
    def spawn_player(self) -> None:
        spawn_pos = Vector(self.renderer.dimensions[0] / 2, self.renderer.dimensions[1] / 2)
        player = Player(self, int_id = 0, position = spawn_pos, velocity = Vector(), can_think = True)
        self.renderer.set_focus(player)
        self.agars.append(player)   
        return 

    # spawns the agars to be used in the simulation
    def spawn_bots(self, num_bots : int = 1) -> None:
        # itterates through the number of agars to be spawned
        for i in range(num_bots):
            # picks out a position to spawn the agar at
            spawn_pos = Vector.random_vector_within_bounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]))
            # constructs the agar object
            bot = DumbBot(self, int_id = i, position = spawn_pos, velocity = Vector(), can_think = True)
            # appends it to the list of agars in the simulation
            self.agars.append(bot)     
        return 

    # spawns the blobs used in the simulation, defaults to one blob
    def spawn_blobs(self, num_blobs : int = 1) -> None:
        # don't spawn more blobs if the simulation has ended
        if (self.is_running == False): return

        # itterates through the number of blobs to be spawned
        for i in range(num_blobs):
            # picks out a position to spawn the agar at
            spawn_pos = Vector.random_vector_within_bounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]))
            # constructs the blob object
            blob = Blob(self, int_id = i, position = spawn_pos)
            # appends it to the list of bobs in the simulation
            self.blobs.append(blob)

        # create the timer for the next blob to spawn
        # within the simulation thread
        self.create_timer(time_interval = (1 / self.blob_spawn_rate), method = self.spawn_blobs)
        return   

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

    """ UPDATES """
    # draws a frame on the interface
    def update(self) -> None:
        # ends the simulation if it has updated the necessary amount of times
        self.frames += 1
        if (self.frames * self.frame_rate > self.run_time):
            self.end()
            return

        # check for any running timers
        if (self.frames in self.frame_callbacks):
            for method in self.frame_callbacks[self.frames]:
                Debug.simulation("Callback to " + method.__name__)
                method()

        # yes, most of these can be done within
        # a single loop
        # check for changes
        self.update_thinkers()
        # set the positions
        self.update_positions()
        # set the sizes
        self.update_sizes()
        # update the window
        self.renderer.update()
        # check for collisions
        self.check_collisions()

        Debug.simulation_update("{0} agars left, and {0} blobs".format(len(self.agars), len(self.blobs)))

        # start a callback to update the next frame at the desired frame rate
        next_update = Timer(self.frame_rate, self.update, args=None, kwargs=None)
        next_update.start()
        return

    # hello
    def update_thinkers(self) -> None:
        for agar in self.agars:
            agar.update_think()
        return

    # set the agar positions
    def update_positions(self) -> None:
        for agar in self.agars:
            # update its position based on its velocity
            agar.update_position(self.frame_rate)
            # check that it is within bounds
            agar.check_within_bounds(self.renderer.dimensions)
        return

    # set the sizes
    def update_sizes(self) -> None:
        for agar in self.agars:
            agar.update_size(self.frame_rate)
        return

    def create_timer(self, time_interval : float = 0, method = None) -> bool:
        if (method == None): return False
        Debug.simulation("Added a timer to call " + method.__name__)
        frames_left = self.convert_time_to_frames(time_interval)
        if (self.frames + frames_left not in self.frame_callbacks):
            self.frame_callbacks[self.frames + frames_left] = []
        self.frame_callbacks[self.frames + frames_left].append(method)
        return True

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
        return
    
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

    """ CONVERSIONS """
    def convert_time_to_frames(self, time_interval : float = 0) -> int:
        return int(math.ceil(time_interval / self.frame_rate))