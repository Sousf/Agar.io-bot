### LIBRARIES ###
import time
import math
import random
import tkinter as gui
from threading import Timer
import pygame as game

### LOCAL MODULES ###
from vectors import Vector

### MAGIC VARIABLES ###

# default agar parameters (used if not specified at initialisation)
MIN_AGAR_SIZE = 20
MAX_AGAR_SIZE = 100
DEFAULT_AGAR_POSITION = Vector(0, 0)
DEFAULT_AGAR_VELOCITY = Vector(0, 0)

# some parameters for controlling stat changes
BASE_SPEED = 500
SPLIT_SPEED = 800
MAX_SPEED = 600
BASE_SIZE_LOSS_RATE = 0.01 # lose a 100th of your size per second
DEFAULT_ID = 0 # not working (need increment to increment the global variable inside initialization)
DEFAULT_THINK_INTERVAL = 1

# default blob parameters (used if not specified at initialisation)
MIN_BLOB_SIZE = 6
MAX_BLOB_SIZE = 15

# time controls for the game, note that these time controls 
# will have to be  modified into a frame time base to be able to simulate at
# faster the real time speeds
SPLIT_CHILD_THINKER_DELAY = 0.75
BASE_MERGE_DELAY = 0.75
DEFAULT_SPLIT_DELAY = 0.3

# The base agar object
# Requires an id (for splitting and merging), size, position, velocity
# Base speed is required to figure out how to scale slowness with size
# Think controls whether it can act (if false, the agar won't be able to do anything)
class Agar():
    def __init__(self, simulation, id = DEFAULT_ID,  
                 size : float = MIN_AGAR_SIZE, 
                 position : Vector = DEFAULT_AGAR_POSITION, 
                 velocity : Vector = DEFAULT_AGAR_VELOCITY, 
                 base_speed : float = BASE_SPEED, 
                 base_size_loss_rate : float = BASE_SIZE_LOSS_RATE,
                 think : bool = True, 
                 think_interval : float = DEFAULT_THINK_INTERVAL,
                 can_split : bool = True, 
                 can_merge : bool = True,
                 rect : game.Rect = None
                 ) -> None:

        # the parent simulation
        self.simulation = simulation

        # set the id of the agar
        if (type(id) == str):
            self.id = id
        else:
            self.id = self.get_type() + str(id)
        # basic parameters
        self.size = size
        self.position = position
        self.delta_position = Vector()
        self.velocity = velocity
        self.base_speed = base_speed
        self.baseSizeLossRate = base_size_loss_rate
        self.rect = rect # the canvas its drawn on

        # stores the subquadrant that the agar is located in for optimization purposes
        # not used currently, but will be!
        self.curr_sub_grid = None
        self.can_split = can_split
        self.can_merge = can_merge
        self.is_eaten = False

        # start the thinker
        self.think_interval = think_interval
        self.start_thinker(think)

        return None

    # starts the thinker, or stops it
    def start_thinker(self, think : bool) -> None:
        # set the state of thinking
        self.think = think
        # launch the thinkers if necessary
        if (self.think): 
            self.on_think()
        return None
    
    # the actions to decide every time the agar thinks
    def on_think(self) -> None:
        # shut down the thinker 
        if (self.think == False): return 

        # update the velocity (i.e choose a direction)
        self.update_velocity()

        # decide whether to split
        self.decide_to_split()

        # start a callback for the next think to occur after an interval
        next_think = Timer(self.think_interval, self.on_think, args=None, kwargs=None)
        next_think.start()
        return None

    # update the position based on the velocity and time passed since the last update
    def update_position(self, timeInterval : float = 0):
        self.delta_position = self.velocity * timeInterval
        self.position = self.position + self.delta_position
        return

    # check that the agar does not go out of bounds
    def check_within_bounds(self, dimensions):
        if (self.position.x >= dimensions[0]):
            self.position.x = dimensions[0]
        elif (self.position.x <= 0):
            self.position.x = 0
        if (self.position.y >= dimensions[1]):
            self.position.y = dimensions[1]
        elif (self.position.y <= 0):
            self.position.y = 0
        return

    # update the velocity (decision dependent on the type of agar)
    def update_velocity(self):
        # handled in extensions
        return

    def update_size(self, time_interval : float = 0):
        self.size = self.size - (self.size * self.baseSizeLossRate * time_interval)
        # overrides the split buffer :(
        # if (self.size > k_minSplitThreshold):
        #    self.canSplit
        return

    def decide_to_split(self):
        # handled in extensions
        return

    # conversion between the size of the agar and its speed
    def convert_size_to_speed(self) -> float:
        return min(MAX_SPEED, self.base_speed / math.sqrt(self.size / MIN_AGAR_SIZE))

    # conversion between the size of the agar and its color
    def convert_size_to_color(self):
        size_ratio = min((self.size) / (MAX_AGAR_SIZE), 0.95)
        color = '#%02x%02x%02x' % (int(size_ratio * 64 + 192), int(size_ratio * 192 + 64), 0)
        return color

    # check for collisions
    def on_collision(self, agar):
        if (self == agar): return
        if (self.id == agar.id): # add the time constraints for merging back together
            self.merge(agar)
        elif (self.size > agar.size):
            self.eat(agar)
        return

    def eat(self, agar):
        self.size = self.size + agar.size / 5
        agar.think = False
        agar.is_eaten = True
        del agar.rect
        return

    def split(self):
        if (self.can_split == False): return
        # constructs the agar object
        agar = self.clone()
        agar.velocity = agar.velocity.normalize() * SPLIT_SPEED
        agar.size *= 0.5
        self.size *= 0.5
        self.can_split = False

        # delay control over the split
        delayed_think = Timer(SPLIT_CHILD_THINKER_DELAY, agar.kick_start_thinker, args=None, kwargs=None)
        # delay the abilitiy for the child agar to merge back
        delayed_merge = Timer(BASE_MERGE_DELAY, agar.enable_merge, args=None, kwargs=None)
        # delay the ability of the parent agar to split? not sure if this is necessary if there is a size cap
        delayed_split = Timer(DEFAULT_SPLIT_DELAY, self.enable_split, args=None, kwargs=None)

        delayed_think.start()
        delayed_merge.start()
        delayed_split.start()

        # appends it to the list of agars in the simulation (not workin)
        # i'd also like to not have to point to the simulation in the agars :(
        agar.rect = self.simulation.renderer.render_agar(agar)
        self.simulation.agars.append(agar)     
        return

    def clone(self):
        return Agar(self.simulation, 
                    id = self.id, 
                    size = self.size, 
                    position = self.position, 
                    velocity = self.velocity, 
                    think = False, 
                    can_split = False, 
                    can_merge = False)

    # essentially the same as merging but
    # gain all the size instead of just a portion
    # and snap to the mid point
    def merge(self, agar):
        if (agar.can_merge == False or self.can_merge == False): return # can't merge until it's buffer is over
        self.size = self.size + agar.size
        #self.position = Vector.midPoint(self.position, agar.position)
        agar.think = False
        agar.is_eaten = True
        del agar.rect
        return

    def kick_start_thinker(self):
        self.start_thinker(True)
        return

    def enable_merge(self):
        self.can_merge = True
        return

    def enable_split(self):
        self.can_split = True
        return

    def get_type(self):
        return "base"
   
# A player controlled agar
# Extends from the base agar
# Requires, additionally, the window that the simulation is being run on
class Player(Agar):

    # update the velocity of the agar to be towards the mouse of the player
    def update_velocity(self) -> None:
        # cannot calculate mouse position without a window
        # if (self.window == None): return

        # get the appropriate mouse coordinates
        mouse_pos = game.mouse.get_pos()
        if (self.simulation.renderer.focus != None):
            focus_point = self.simulation.renderer.focus.position
        else:
            focus_point = Vector()
        mouseVec = Vector(mouse_pos[0], mouse_pos[1])

        # get the direction between the agar and the mouse for an unfocused player        
        direction = (mouseVec - self.simulation.renderer.center) - (self.position - focus_point)

        # check that the mouse is far enough away to warrant movement
        if (direction.magnitude() <= 20):
            self.velocity = Vector()
        else:
            self.velocity = direction.normalize() * self.convert_size_to_speed()
        return None

    def decide_to_split(self):
        pressed_keys = game.key.get_pressed()
        for key_constant, pressed in enumerate(pressed_keys): 
            if pressed:
                self.split()
        return

    def clone(self):
        # constructs the agar object
        return Player(self.simulation, 
                      id = self.id, 
                      size = self.size, 
                      position = self.position, 
                      velocity = self.velocity, 
                      think = False, 
                      think_interval = self.think_interval, 
                      can_split = False, 
                      can_merge = False)
        
    def get_type(self):
        return "player"

# A 'Dumb' Agar bot that randomly picks a direction to move in
# Extends from the base agar
class DumbBot(Agar):

    # randomly select a direction to move in
    # when they split, both agars need to be moving towards a certain point
    # the agars that have the same parent need to be able to communicate with each other (?)
    # right now the child agars move independently of the parent which is incorrect
    def update_velocity(self):
        self.velocity = Vector.random_normalized_vector() * self.convert_size_to_speed()
        return

    def decide_to_split(self):
        if (random.random() > 0.95):
            self.split()
        return

    def clone(self):
        # constructs the agar object
        return DumbBot(self.simulation, 
                       id = self.id, 
                       size = self.size, 
                       position = self.position, 
                       velocity = self.velocity, 
                       think = False, 
                       think_interval = self.think_interval, 
                       can_split = False, 
                       can_merge = False)
         
    def get_type(self):
        return "dumbbot"

# The 'Blob' Agars scattered around the map that stay still and exist only to be eaten
# Extends from the base agar
# Randomly vary their size
class Blob(Agar):
    def __init__(self, simulation, 
                 id : int = DEFAULT_ID, 
                 min_size : float = MIN_BLOB_SIZE, 
                 max_size : float = MAX_BLOB_SIZE,
                 position : Vector = DEFAULT_AGAR_POSITION, 
                 rect : game.Rect = None
                 ) -> None:

        # randomly generate the size of the blob
        self.min_size = min_size
        self.max_size = max_size
        size = random.random() * (max_size - min_size) + min_size

        # make sure this isn't thinking (otherwise it would be very heavy)
        self.think = False

        # initialize the rest of the agar
        Agar.__init__(self, simulation, id, size, position, Vector(), 0, 0, False, 1000, rect = rect)
        return None

    # override the coloring of this agar to distinguish it
    def convert_size_to_color(self):
        size_ratio = (self.size - self.min_size) / (self.max_size - self.min_size)
        color = '#%02x%02x%02x' % (int(size_ratio * 192 + 64), int(size_ratio * 64 + 192), 0)
        return color

    def clone(self):
        return self

    def get_type(self):
        return "blob"

