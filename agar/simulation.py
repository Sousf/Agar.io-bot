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
from agar import SmartBot
from agar import Blob
from agar import Virus
from vectors import Vector
from grid import Grid
from debug import Debug
from renderer import Renderer

""" MAGIC VARIABLES """
# default values for simulation (if not specified on initialization)
RENDER = True
DEFAULT_NUM_BOTS = 1
DEFAULT_ENEMY_RESPAWN_TIME = 0.1
DEFAULT_NUM_VIRUSES = 0
DEFAULT_VIRUS_SPAWN_RATE = 0.000001 # viruses per second
DEFAULT_NUM_BLOBS = 250
DEFAULT_BLOB_SPAWN_RATE = 1 # blob batches per second
BLOB_BATCH_SIZE = 10
DEFAULT_FRAME_RATE = 60
DEFAULT_RUN_TIME = -1
DEFAULT_MAP_HEIGHT = 4000
DEFAULT_MAP_WIDTH = 8000
DEFAULT_WINDOW_HEIGHT = int(1080 / 2)
DEFAULT_WINDOW_WIDTH = int(1920 / 2)

""" BASE SIMULATOR """
class Simulation():
    """
    Runs a simulation for the duration of the run time (note, the run time is calculated on the agar's physics 
    (i.e. it matches the timing that agar's update at so that the simulation completes, 
    regardless of if this matches real time values)
    """
    def __init__(self, caption : str = "Base Simulation",
                 render : bool = RENDER,
                 player : bool = False,
                 num_bots : int = DEFAULT_NUM_BOTS,
                 num_viruses : int = DEFAULT_NUM_VIRUSES,
                 virus_spawn_rate : float = DEFAULT_VIRUS_SPAWN_RATE,
                 num_blobs : int = DEFAULT_NUM_BLOBS, 
                 blob_spawn_rate : float = DEFAULT_BLOB_SPAWN_RATE,
                 map_dimensions : tuple = (DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT),
                 window_dimensions : tuple = (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT),
                 frame_rate : float = DEFAULT_FRAME_RATE, 
                 run_time : float = DEFAULT_RUN_TIME,
                 internal_update = False
                 ):

        self.caption = caption

        # sets the base parameters
        self.virus_spawn_rate = virus_spawn_rate
        self.blob_spawn_rate = blob_spawn_rate
        self.map_dimensions = map_dimensions
        self.frame_rate = frame_rate
        self.frames = 0
        self.frame_callbacks = {}
        self.run_time = run_time
        self.is_running = True
        self.next_update = None
        self.delayed_end = None
        self.render = render
        self.clock = game.time.Clock()
        self.internal_update = internal_update

        self.switch = 2 * (round(random.random()) - 0.5)

        # used for collisions
        # self.grid = Grid(0, width, height, 10)

        Debug.simulation("Running " + self.caption + " for {0} seconds at {1:.2f} frames per second".format(self.run_time, (1 / self.frame_rate)))
        # constructs the interface
        self.vision_dimensions = (window_dimensions[0], window_dimensions[1])
        self.vision_center = Vector(window_dimensions[0] / 2, window_dimensions[1] / 2)
        if (self.render):
           self.renderer = Renderer(self, width = window_dimensions[0], height = window_dimensions[1])

        # spawn the player if necessary
        self.agars = []
        if (player): 
            self.spawn_player()
        else:
            self.spawn_ai()
        Debug.simulation("Spawned a player")
        
        # spawns the agars to be used in the simulation
        self.spawn_bots(num_bots)
        Debug.simulation("Spawned {0} agars".format(num_bots))

        # spawns the agars to be used in the simulation
        self.spawn_viruses(num_viruses)
        Debug.simulation("Spawned {0} agars".format(num_viruses))
        
        # spawns the initial set of blobs, and then starts spawning blobs every so often
        self.blobs = []
        self.spawn_blobs(num_blobs)
        Debug.simulation("Spawned {0} blobs".format(num_blobs))

        # begins the simulation
        self.start()
        self.delayed_end = None
        return
    
    """ SPAWNERS """
    # spawns the player to be used in the simulation
    def spawn_player(self) -> None:
        spawn_pos = Vector(self.map_dimensions[0] / 2, self.map_dimensions[1] / 2)
        player = Player(self, int_id = 0, position = spawn_pos, can_think = True)
        self.agars.append(player)  
        return 

    # spawns the player to be used in the simulation
    def spawn_ai(self) -> None:
        spawn_pos = Vector(self.map_dimensions[0] / 2, self.map_dimensions[1] / 2)
        player = SmartBot(self, int_id = 0, position = spawn_pos, can_think = True) 
        self.agars.append(player)  
        return 

    # spawns the agars to be used in the simulation
    def spawn_bots(self, num_bots : int = 1) -> None:
        # itterates through the number of agars to be spawned
        for i in range(num_bots):
            # picks out a position to spawn the agar at
            spawn_pos = Vector.random_vector_within_bounds((0, self.map_dimensions[0]), (0, self.map_dimensions[1]))
            # constructs the agar object
            spawn_pos = Vector(  self.map_dimensions[0] / 2 + (self.switch * 300), 0)

            bot = DumbBot(self, int_id = i, position = spawn_pos, can_think = True, mass = 500)
            # appends it to the list of agars in the simulation
            self.agars.append(bot)
            
        # self.create_timer(time_interval = (1 / DEFAULT_ENEMY_RESPAWN_TIME), method = self.spawn_bots)

        return 
    
    # spawns the viruses to be used in the simulation
    def spawn_viruses(self, num_viruses : int = 1) -> None:
        # itterates through the number of agars to be spawned
        for i in range(num_viruses):
            # picks out a position to spawn the agar at
            spawn_pos = Vector.random_vector_within_bounds((0, self.map_dimensions[0]), (0, self.map_dimensions[1]))
            # constructs the agar object
            virus = Virus(self, int_id = i, position = spawn_pos)
            # appends it to the list of agars in the simulation
            self.agars.append(virus)     

        #self.create_timer(time_interval = (1 / self.virus_spawn_rate), method = self.spawn_viruses)
        return 

    # spawns the blobs used in the simulation, defaults to one blob
    def spawn_blobs(self, num_blobs : int = BLOB_BATCH_SIZE) -> None:
        # don't spawn more blobs if the simulation has ended
        if (self.is_running == False): return
            
        # itterates through the number of blobs to be spawned
        for i in range(num_blobs):
            # picks out a position to spawn the agar at
            # spawn_pos = Vector.random_vector_within_bounds((0, self.map_dimensions[0]), (0, self.map_dimensions[1]))
            # constructs the blob object
            # spawn_pos = Vector((self.map_dimensions[0] / 2) - 100, 0)
            spawn_pos = Vector( (self.map_dimensions[0] / 2) * (1 - self.switch * i / num_blobs), 0)

            blob = Blob(self, int_id = i, position = spawn_pos)
            # appends it to the list of bobs in the simulation
            self.blobs.append(blob)

        # create the timer for the next blob to spawn
        # within the simulation thread
        # self.create_timer(time_interval = (1 / self.blob_spawn_rate), method = self.spawn_blobs)
        return   

    """ CONTROLS """
    # start the simulation
    def start(self):
        Debug.simulation("Starting rendering")
        self.update_rects()
        if (self.render):
            self.renderer.start()

        if (self.internal_update):
            self.update()
        return

    # shut down the simulation
    def end(self):
        Debug.simulation("Ending rendering")
        for agar in self.agars:
            agar.disable()
        self.agars = []
        self.is_running = False

        # fail safe for force quitting in between simulation end and renderer closing
        if (self.delayed_end != None and self.delayed_end.is_alive()): self.delayed_end.cancel()
        # cancels the next update if the simulation has not completed
        if (self.next_update != None and self.next_update.is_alive()): self.next_update.cancel()

        # closes the window after a short buffer (not working)
        if (self.render):
            self.renderer.close()
        return

    """ UPDATES """
    # draws a frame on the interface
    def update(self) -> None:
        self.frames += 1
        # ends the simulation if something external has caused it to stop running
        if (self.is_running == False): return
        # or ends the simulation if it has run its course
        elif (self.run_time!= -1 and self.frames * self.frame_rate > self.run_time):
            #self.delayed_end = Timer(3, self.end, args=None, kwargs=None)
            #self.delayed_end.start()
            self.is_running = False
            self.end()
            return

        # check for any running timers
        if (self.frames in self.frame_callbacks):
            for method in self.frame_callbacks[self.frames]:
                if (method != None):
                    Debug.simulation("Callback to " + method.__name__)
                    method()

        # yes, most of these can be done within
        # a single loop
        # update the rects (colliders)
        self.update_rects()
        # set the sizes
        self.update_sizes()
        # check for changes
        self.update_thinkers()
        # set the positions
        self.update_motions()

        # check for collisions
        self.check_collisions()
        # update the window
        if (self.render):
            self.renderer.update()


        Debug.simulation_update("{0} agars left, and {0} blobs".format(len(self.agars), len(self.blobs)))

        # start a callback to update the next frame at the desired frame rate
        # self.next_update = Timer(self.frame_rate, self.update, args=None, kwargs=None)
        # self.next_update.start()
        return

    # updates the thinkers
    def update_thinkers(self) -> None:
        for agar in self.agars:
            agar.update_think()
        return

    # set the agar positions
    def update_motions(self) -> None:
        for agar in self.agars:
            agar.update_velocity(1/self.frame_rate)
            # update its position based on its velocity
            agar.update_position(1/self.frame_rate)
            # check that it is within bounds
            agar.check_within_bounds(self.map_dimensions)
        return

    # set the sizes
    def update_sizes(self) -> None:
        for agar in self.agars:
            agar.update_size(1/self.frame_rate)
        return

    # updates the rects (colliders)
    def update_rects(self) -> None:
        # don't think i need to update blobs
        # draw the blobs first
        for blob in self.blobs:
            blob.rect = game.Rect(blob.position.x - blob.size, blob.position.y - blob.size, 2 * blob.size, 2 * blob.size)
        for agar in self.agars:
            agar.rect = game.Rect(agar.position.x - agar.size, agar.position.y - agar.size, 2 * agar.size, 2 * agar.size)
            # doing it this way in case we wanna add more smart bots
             # change this to display whatever info we want
             # e.g. agar's id, size, number of eaten things, speed, current position etc

        pass

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
    def check_collision(self, agar : Agar, agars : list, colliders : list):
        # returns the indices of the all the collisions found
        collision_indices = agar.rect.collidelistall(colliders)

        # runs through all the collisions
        for index in collision_indices:
            agar.on_collision(agars[index])
            if (agars[index].is_eaten):
                # remove the agar collider that was eaten from both lists if it was eaten
                del agars[index]
                del colliders[index]
                """
                we're editing the active collider list here
                this is going to make the list of collision indices useless
                as they point to locations within this active collider list
                breaking here to avoid the issue
                but this means only one collision that results in eating can be detected per frame
                im sure there is a more elegant solution
                """
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
        return int(math.ceil(time_interval * self.frame_rate))