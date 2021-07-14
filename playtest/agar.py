""" IMPORTED LIBRARIES """
import time
import math
import random
import tkinter as gui
from threading import Timer
import pygame as game

""" LOCAL MODULES """
from vectors import Vector
from debug import Debug

""" GLOBAL VARIABLES """
# default agar parameters (used if not specified at initialisation)
MIN_AGAR_SIZE = 20
MAX_AGAR_SIZE = 100
DEFAULT_AGAR_POSITION = Vector(0, 0)
DEFAULT_AGAR_VELOCITY = Vector(0, 0)

# some parameters for controlling stat changes
BASE_SPEED = 500
SPLIT_SPEED = 1500
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

""" AGAR OBJECTS """
class Agar():
    """ 
    Requires an id (for splitting and merging), size, position, velocity
    Base speed is required to figure out how to scale slowness with size
    Think controls whether it can act (if false, the agar won't be able to do anything)
    """
    def __init__(self, simulation, id = DEFAULT_ID,
                 is_parent = True,
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
        self.id = self.convert_to_id(id)
        
        # basic parameters
        self.is_parent = is_parent;
        self.size = size
        self.position = position
        self.delta_position = Vector()
        self.velocity = velocity
        self.base_speed = base_speed
        self.base_size_loss_rate = base_size_loss_rate
        self.rect = rect # the canvas its drawn on

        # stores the subquadrant that the agar is located in for optimization purposes
        # not used currently, but will be!
        self.curr_sub_grid = None
        self.can_split = can_split
        self.can_merge = can_merge
        self.is_eaten = False

        self.delayed_think = None
        self.delayed_merge = None
        self.delayed_split = None

        # start the thinker
        self.think_interval = think_interval
        self.start_thinker(think)

        return

    """ THINKER """
    # starts the thinker, or stops it
    def start_thinker(self, think : bool) -> None:
        # set the state of thinking
        self.think = think
        # launch the thinkers if necessary
        if (self.think): 
            self.on_think()
        return
    
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
        return

    """ PASSIVE ACTIONS (called by simulation) """
    # update the position based on the velocity and time passed since the last update
    def update_position(self, timeInterval : float = 0) -> None:
        self.delta_position = self.velocity * timeInterval
        self.position = self.position + self.delta_position
        return

    # update the size lost per frame
    def update_size(self, time_interval : float = 0) -> float:
        self.size = max(MIN_AGAR_SIZE, self.size - (self.size * self.base_size_loss_rate * time_interval));
        # overrides the split buffer :(
        if (self.delayed_split == None):
            if (self.size < 2 * MIN_AGAR_SIZE):
               self.can_split = False
            else:
                self.can_split = True
        return self.size

    # check that the agar does not go out of bounds
    def check_within_bounds(self, dimensions : tuple) -> None:
        if (self.position.x >= dimensions[0]):
            self.position.x = dimensions[0]
        elif (self.position.x <= 0):
            self.position.x = 0
        if (self.position.y >= dimensions[1]):
            self.position.y = dimensions[1]
        elif (self.position.y <= 0):
            self.position.y = 0
        return

    """ ACTIVE ACTIONS (called by individual agar) """
    # update the velocity (decision dependent on the type of agar)
    def update_velocity(self) -> None:
        # handled in extensions
        return

    # decide to split (decision dependent on the type of agar)
    def decide_to_split(self) -> bool:
        # handled in extensions
        return False

    # run through the process for splitting mechanic
    def split(self) -> None:
        if (self.can_split == False): return
        Debug.agar(self.id + " is splitting")

        # constructs the agar object
        agar = self.clone()
        agar.velocity = agar.velocity.normalize() * SPLIT_SPEED
        agar.size *= 0.5
        self.size *= 0.5
        self.can_split = False

        # delay control over the split
        agar.delayed_think = Timer(SPLIT_CHILD_THINKER_DELAY, agar.kick_start_thinker, args=None, kwargs=None)
        # delay the abilitiy for the child agar to merge back
        agar.delayed_merge = Timer(BASE_MERGE_DELAY, agar.enable_merge, args=None, kwargs=None)
        # delay the ability of the parent agar to split? not sure if this is necessary if there is a size cap
        self.delayed_split = Timer(DEFAULT_SPLIT_DELAY, self.enable_split, args=None, kwargs=None)

        agar.delayed_think.start()
        agar.delayed_merge.start()
        self.delayed_split.start()

        # appends it to the list of agars in the simulation (not workin)
        # i'd also like to not have to point to the simulation in the agars :(
        agar.rect = self.simulation.renderer.render_agar(agar)
        self.simulation.agars.append(agar)     
        return

    # reconstructs the agar object 
    # (overriden in extensions for particular types of agars)
    # can be done in a neater way
    def clone(self):
        return Agar(self.simulation, 
                    id = self.id, 
                    is_parent = False,
                    size = self.size, 
                    position = self.position, 
                    velocity = self.velocity, 
                    think = False, 
                    can_split = False, 
                    can_merge = False)

    """ COLLISIONS """
    # check for collisions
    def on_collision(self, agar) -> None:
        if (self == agar): return
        if (self.id == agar.id): # add the time constraints for merging back together
            self.merge(agar)
        elif (self.size > agar.size):
            self.eat(agar)
        return

    # run through the process for eating another agar
    def eat(self, agar) -> None:
        Debug.agar(self.id + " eats " + agar.id + ", gaining {0:.2f} size".format(agar.size / 5))
        self.size = self.size + agar.size / 5
        agar.disable()
        return

    # run through the process of merging with another agar
    def merge(self, agar) -> None:
        # essentially the same as eating but
        # gain all the size instead of just a portion
        # and snap to the mid point
        if (agar.can_merge == False or self.can_merge == False or self.is_parent == False): return # can't merge until it's buffer is over
        Debug.agar(self.id + " merges  back, gaining {0:.2f} size".format(agar.size))
        self.size = self.size + agar.size
        # self.position = Vector.mid_point(self.position, agar.position) # doesn't look pretty
        agar.disable()
        return

    """ SWITCHES """
    def kick_start_thinker(self):
        self.start_thinker(True)
        return

    def enable_merge(self):
        self.can_merge = True
        self.delayed_merge = None;
        return

    def enable_split(self):
        self.can_split = True
        self.delayed_split = None
        return

    def disable(self) -> None:
        self.think = False
        self.is_eaten = True
        del self.rect
        if (self.delayed_think != None): self.delayed_think.cancel()
        if (self.delayed_merge != None): self.delayed_merge.cancel()
        if (self.delayed_split != None): self.delayed_split.cancel()
        return None


    """ CONVERSIONS """
    # conversion between the size of the agar and its speed
    def convert_size_to_speed(self) -> float:
        return min(MAX_SPEED, self.base_speed / math.sqrt(self.size / MIN_AGAR_SIZE))

    # conversion between the size of the agar and its color
    def convert_size_to_color(self) -> str:
        size_ratio = min((self.size) / (MAX_AGAR_SIZE), 0.95)
        color = '#%02x%02x%02x' % (int(size_ratio * 64 + 192), int(size_ratio * 192 + 64), 0)
        return color

    # conversion that outputs the id
    def convert_to_id(self, id = None) -> str:
        if (type(id) == str):
            str_id = str(id);
        else:
            str_id = self.type + str(id)
        return str_id

    # should probably make this an enum
    @property
    def type(self):
        return "base"
   
class Player(Agar):
    """ A player controlled agar """

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

    # split if the keyboard is pressed
    def decide_to_split(self):
        pressed_keys = game.key.get_pressed()
        for key_constant, pressed in enumerate(pressed_keys): 
            if pressed:
                self.split()
        return

    # reconstructs the agar object
    def clone(self):
        return Player(self.simulation, 
                      id = self.id,
                      is_parent = False,
                      size = self.size, 
                      position = self.position, 
                      velocity = self.velocity, 
                      think = False, 
                      think_interval = self.think_interval, 
                      can_split = False, 
                      can_merge = False)

    # override the coloring of this agar to distinguish it
    def convert_size_to_color(self):
        size_ratio = min((self.size) / (MAX_AGAR_SIZE), 0.95)
        color = '#%02x%02x%02x' % (int(size_ratio * 128 + 127), 0, int(size_ratio * 128 + 127))
        return color

    # should probably make this an enum 
    @property
    def type(self):
        return "player"

class DumbBot(Agar):
    """ A 'Dumb' Agar bot that randomly picks a direction to move in """

    # randomly select a direction to move in
    def update_velocity(self):
        # when they split, both agars need to be moving towards a certain point
        # the agars that have the same parent need to be able to communicate with each other (?)
        # right now the child agars move independently of the parent which is incorrect
        self.velocity = Vector.random_normalized_vector() * self.convert_size_to_speed()
        return

    # randomly decide to split
    def decide_to_split(self):
        if (random.random() > 0.95):
            self.split()
        return

    # reconstructs the agar object
    def clone(self):
        return DumbBot(self.simulation, 
                       id = self.id, 
                       is_parent = False,
                       size = self.size, 
                       position = self.position, 
                       velocity = self.velocity, 
                       think = False, 
                       think_interval = self.think_interval, 
                       can_split = False, 
                       can_merge = False)

    # override the coloring of this agar to distinguish it
    def convert_size_to_color(self):
        size_ratio = min((self.size) / (MAX_AGAR_SIZE), 0.95)
        color = '#%02x%02x%02x' % (int(size_ratio * 64 + 192), int(size_ratio * 207 + 48), 0)
        return color
    
    # should probably make this an enum 
    @property        
    def type(self):
        return "dumbbot"

class Blob(Agar):
    """ The 'Blob' Agars scattered around the map that stay still and exist only to be eaten, with randomly vared size """

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
        Agar.__init__(self, simulation, 
                      id = id, 
                      is_parent = True, 
                      size = size, 
                      position = position, 
                      velocity = Vector(), 
                      base_speed = 0, 
                      base_size_loss_rate = 0, 
                      think = False, 
                      think_interval = 1000, 
                      rect = rect)
        return None

    # override the coloring of this agar to distinguish it
    def convert_size_to_color(self):
        size_ratio = (self.size - self.min_size) / (self.max_size - self.min_size)
        color = '#%02x%02x%02x' % (int(size_ratio * 192 + 64), int(size_ratio * 64 + 192), 0)
        return color

    # blobs can't clone themselves
    def clone(self):
        return self

    # should probably make this an enum
    @property
    def type(self):
        return "blob"

