""" IMPORTED LIBRARIES """
import time
import math
import random
import tkinter as gui
from threading import Timer
import pygame as game
from dataclasses import dataclass

""" LOCAL MODULES """
from vectors import Vector
from color import Color
from debug import Debug

""" GLOBAL VARIABLES """
# default agar parameters (used if not specified at initialisation)
DEFAULT_ID = 0

# vectors
DEFAULT_AGAR_POSITION = Vector(0, 0)
DEFAULT_AGAR_VELOCITY = Vector(0, 0)

# controls the speed
ACCELERATION = 2500
BASE_SPEED = 500
SPLIT_SPEED = 1000
EJECT_SPEED = 1500
MAX_SPEED = 600

# controls the size for agars
MIN_AGAR_SIZE = 20
MAX_AGAR_SIZE = 100
EAT_SIZE_THRESHOLD = 1.25
BASE_SIZE_LOSS_RATE = 0.02 # lose a 50th of your size per second
EJECTED_MASS_FACTOR = 0.18

# controls the size for blobs
MIN_BLOB_SIZE = 6
MAX_BLOB_SIZE = 8
BLOB_COLORS = [(255, 0, 0), (255)]

# all time controls relative to a frame rate of 60

# time controls for the merging
BASE_MERGE_DELAY = 10 # should be 30 for irl agar io
MERGE_DELAY_FACTOR = 0.0233

# time controls for the splitting
SPLIT_CHILD_THINKER_DELAY = 0.2
DEFAULT_SPLIT_DELAY = 0.3

# time controls for ejection
DEFAULT_EJECT_DELAY = 0.3
EJECT_CHILD_THINKER_DELAY = 0.3

""" AGAR OBJECT """
class Agar():
    """ 
    Requires an id (for splitting and merging), size, position, velocity
    Base speed is required to figure out how to scale slowness with size
    Think controls whether it can act (if false, the agar won't be able to do anything)
    """
    _color = Color()
    def __init__(self, simulation, 
                 int_id = DEFAULT_ID,
                 size : float = MIN_AGAR_SIZE,
                 size_loss_rate : float = BASE_SIZE_LOSS_RATE,
                 target_point : Vector = Vector(),
                 position : Vector = DEFAULT_AGAR_POSITION, 
                 speed : float = BASE_SPEED, 
                 rect : game.Rect = None,
                 color_gradient : tuple = None,
                 can_eat : bool = True,
                 can_think : bool = True, 
                 can_split : bool = True, 
                 can_merge : bool = True,
                 can_eject : bool = False,
                 parent = None,
                 is_eaten : bool = False
                 ) -> None:

        # the parent simulation
        self.simulation = simulation

        # set the integer id of the agar
        self.int_id = int_id
        
        # size
        self.size = size
        self.size_loss_rate = size_loss_rate

        # motion  
        self.target_point = target_point
        self.position = position
        self.delta_position = Vector()
        self.velocity = Vector()
        self.delta_velocity = Vector()
        self._speed = speed

        # rendering
        self.rect = rect
        if (color_gradient == None):
            color_gradient = (self._color.lightest_shade, self._color.middle_shade, self._color.darkest_shade)
        self.color_gradient = color_gradient

        # actions
        self.can_think = can_think
        self.can_eat = can_eat
        self.can_split = can_split
        self.can_merge = can_merge
        self.can_eject = can_eject

        # family
        self.parent = parent
        self.children = [] # not using currently

        # states
        self.is_eaten = is_eaten

        # delays
        self.delayed_think = False
        self.delayed_merge = False
        self.delayed_split = False
        self.delayed_eject = False
        return

    """ UPDATES """
    # the actions to decide every time the agar thinks
    def update_think(self) -> bool:
        # shut down the thinker 
        if (self.can_think == False): 
            return False

        # decide a direction to travel in
        self.decide_target_point()
        # decide whether to split
        self.decide_to_split()
        # decide whether to eject
        self.decide_to_eject()
        return True

    # update the velocity based on the acceleration and time passed since the last update
    def update_velocity(self, time_interval : float = 0) -> Vector:
        target_direction = self.target_point - self.position
        # snap this for cohesion
        if (target_direction.magnitude() < 20):
            target_velocity = Vector()
        else:
            target_velocity = target_direction.normalize() * self.speed
        # snap this for cohesion
        if ((target_velocity - self.velocity).magnitude() < time_interval * ACCELERATION):
            self.delta_velocity = Vector()
            self.velocity = target_velocity
        else:
            self.delta_velocity = (target_velocity - self.velocity).normalize() * time_interval * ACCELERATION
            self.velocity = self.velocity + self.delta_velocity
        return self.velocity

    # update the position based on the velocity and time passed since the last update
    def update_position(self, time_interval : float = 0) -> Vector:
        self.delta_position = self.velocity * time_interval
        self.position = self.position + self.delta_position
        return self.position

    # update the size lost based on time passed since last update
    def update_size(self, time_interval : float = 0) -> float:
        self.size = max(MIN_AGAR_SIZE, self.size - (self.size * self.size_loss_rate * time_interval));
        # check whether the agar is over the splitting/ejecting threshold
        self.check_split()     
        self.check_eject()
        return self.size

    """ DECISIONS """
    # update the velocity (decision dependent on the type of agar)
    def decide_target_point(self) -> None:
        # handled in extensions
        return

    # decide to split (decision dependent on the type of agar)
    def decide_to_split(self) -> bool:
        # handled in extensions
        return False

    # decide to split (decision dependent on the type of agar)
    def decide_to_eject(self) -> bool:
        # handled in extensions
        return False

    """ ACTIONS """
    # run through the process for splitting mechanic
    def split(self) -> None:
        if (self.can_split == False): return
        Debug.agar(self.id + " is splitting")

        # splits the agar
        clone = self.split_clone()   
        self.can_split = False

        # slight delay before gaining control
        # clone.delayed_think = self.simulation.create_timer(time_interval = SPLIT_CHILD_THINKER_DELAY, method = clone.enable_think)
        
        # delay before this can merge back to the parent
        clone.delayed_merge = self.simulation.create_timer(time_interval = clone.merge_cooldown, method = clone.enable_merge)
        
        # delay before these can split again
        clone.delayed_split = self.simulation.create_timer(time_interval = DEFAULT_SPLIT_DELAY, method = clone.enable_split)
        self.delayed_split = self.simulation.create_timer(time_interval = DEFAULT_SPLIT_DELAY, method = self.enable_split)

        # appends it to the list of agars in the simulation
        self.simulation.agars.append(clone)     
        return

    def eject(self) -> None:
        if (self.can_eject == False): return
        Debug.agar(self.id + " is ejecting")

        # constructs the agar object
        clone = self.eject_clone()  
        self.can_eject = False

        # delay before the blob stops moving
        clone.delayed_think = self.simulation.create_timer(time_interval = EJECT_CHILD_THINKER_DELAY, method = clone.disable_think)

        # delay before the parent can eject again 
        self.delayed_eject = self.simulation.create_timer(time_interval = DEFAULT_EJECT_DELAY, method = self.enable_eject)

        # can almost instantly merge back
        clone.delayed_merge = False
        # so that this agar will never be able to split
        clone.delayed_split = True

        # appends it to the list of agars in the simulation
        self.simulation.agars.append(clone)     
        return

    # clones the object at half size
    def split_clone(self):
        clone = type(self)(self.simulation, 
                    int_id = self.int_id, 
                    size = self.size,
                    color_gradient = self.color_gradient,
                    target_point = self.target_point,
                    position = self.position,
                    speed = self._speed,
                    can_think = True, 
                    can_split = False, 
                    can_merge = False,
                    parent = self)
        clone.velocity = self.velocity.normalize() * SPLIT_SPEED # no acceleration on start up
        clone.size *= 0.5
        self.size *= 0.5
        clone.position = self.position + (self.velocity.normalize() * (self.size + clone.size + 5))
        return clone

    # clones the object as a blob with a fraction of the size
    def eject_clone(self):
        clone = Blob(self.simulation, 
                     int_id = self.int_id, 
                     min_size = self.size, max_size = self.size,
                     color_gradient = self.color_gradient,
                     position =  self.position)
        clone.can_think = False
        clone.target_point = self.target_point
        #clone._speed = SPLIT_SPEED
        clone.velocity = self.velocity.normalize() * EJECT_SPEED
        clone.size = self.size * EJECTED_MASS_FACTOR
        self.size = self.size * (1 - EJECTED_MASS_FACTOR)
        clone.position = self.position + (self.velocity.normalize() * (self.size + clone.size + 5))
        return clone

    """ COLLISIONS """
    # check for collisions
    def on_collision(self, agar) -> None:
        # cannot collide with self
        if (self.can_eat == False or self == agar): 
            return
        # need to cover up to center of the agar
        elif (self.encompasses(agar) == False):
            return

        # can always eat blobs
        if (type(agar) == Blob):
            self.eat(agar)
        # for collisions between the same agar we merge
        elif (self.id == agar.id):
            if (self.parent == None and self.can_merge == True and agar.can_merge == True):
                self.merge(agar)
            elif (self.parent == None):
                self.bounce(agar)
        # for collisions between different agars attempt to eat
        else:
            if (self.size >= EAT_SIZE_THRESHOLD * agar.size):
                self.eat(agar)
            else:
                self.bounce(agar)
        return

    # check if an agar encompasses a certain point
    def encompasses(self, agar : tuple) -> bool:
        return self.rect.collidepoint(agar.rect.center)

    # run through the process for eating another agar
    def eat(self, agar) -> None:
        Debug.agar(self.id + " eats " + agar.id + ", gaining {0:.2f} size".format(agar.size / 5))
        self.size = self.size + agar.size / 2
        agar.disable()
        return

    # run through the process of merging with another agar
    def merge(self, agar) -> None:
        Debug.agar(self.id + " merges  back, gaining {0:.2f} size".format(agar.size))
        self.size = self.size + agar.size
        agar.disable()
        return

    def bounce(self, agar) -> None:
        perimeter = (agar.position - self.position).normalize() * (max(self.size, agar.size) + 2)
        agar.position = self.position + perimeter
        return

    """ SWITCHES """
    # disable the whole agar
    def disable(self) -> None:
        self.can_think = False
        self.is_eaten = True
        del self.rect
        return

    # position
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

    # thinking
    def enable_think(self):
        self.can_think = True
        self._speed = BASE_SPEED
        self.delayed_think = False
        return

    def disable_think(self):
        self.can_think = False
        self.delayed_think = False
        return

    # merging
    def enable_merge(self):
        self.can_merge = True
        self.delayed_merge = False;
        return

    # splitting
    def check_split(self):
        if (self.delayed_split == False):
            if (self.size < 2 * MIN_AGAR_SIZE):
               self.can_split = False
            else:
                self.can_split = True
        return

    def enable_split(self):
        self.can_split = True
        self.delayed_split = False
        return

    # ejecting
    def check_eject(self):
        if (self.delayed_eject == False):
            if (self.size < 2 * MIN_AGAR_SIZE):
               self.can_eject = False
            else:
                self.can_eject = True
        return

    def enable_eject(self):
        self.can_eject = True
        self.delayed_eject = False
        return


    """ CONVERSIONS """
    # conversion between the size of the agar and its speed
    @property
    def speed(self) -> float:
        if (self.can_think == False):
            return self._speed
        mass = self.size / 10
        return min(MAX_SPEED, self._speed * mass / math.pow(mass, 1.44))

    # conversion between the size of the agar and its speed
    @property
    def merge_cooldown(self) -> float:
        return BASE_MERGE_DELAY + (MERGE_DELAY_FACTOR * self.size)

    # conversion that outputs the id
    @property
    def id(self) -> str:
        str_id = type(self).__name__ + str(self.int_id)
        return str_id

class Player(Agar):
    """ A player controlled agar """
    _color = Color.BLUE()

    # update the velocity of the agar to be towards the mouse of the player
    def decide_target_point(self) -> None:
        self.target_point = self.get_mouse_relative_pos()
        return

    # split if the keyboard is pressed
    def decide_to_split(self) -> None:
        if (self.check_key(game.K_SPACE)):
            self.split()
            return True
        return False

    # split if the keyboard is pressed
    def decide_to_eject(self) -> None:
        if (self.check_key(game.K_w)):
            self.eject()
            return True
        return False

    def check_key(self, key) -> bool:
        pressed_keys = game.key.get_pressed()
        return pressed_keys[key]


    def get_mouse_relative_pos(self):
        # get the appropriate mouse coordinates
        mouse_relative_pos = game.mouse.get_pos()
        mouse_vector = Vector(mouse_relative_pos[0], mouse_relative_pos[1])

        # get the absolute mouse position
        if (self.parent == None):     
            mouse_absolute_pos = mouse_vector + self.position - self.simulation.renderer.center
        else:
            mouse_absolute_pos = mouse_vector + self.parent.position - self.simulation.renderer.center

        return mouse_absolute_pos

class DumbBot(Agar):
    """ A 'Dumb' Agar bot that randomly picks a direction to move in """
    _color = Color.RED()

    # randomly select a direction to move in
    def decide_target_point(self) -> None:
        # when they split, both agars need to be moving towards a certain point
        # the agars that have the same parent need to be able to communicate with each other (?)
        # right now the child agars move independently of the parent which is incorrect
        vision_bounds = self.simulation.renderer.dimensions
        if (random.random() > 0.95):
            self.target_point = Vector.random_vector_within_bounds([0, vision_bounds[0]], [0, vision_bounds[1]]) + self.position - self.simulation.renderer.center
        return

    # randomly decide to split
    def decide_to_split(self) -> bool:
        if (random.random() > 0.95):
            self.split()
            return True
        return False

    # randomly decide to eject
    def decide_to_eject(self) -> bool:
        if (random.random() > 0.95):
            self.eject()
            return True
        return False

class Blob(Agar):
    """ The 'Blob' Agars scattered around the map that stay still and exist only to be eaten, with randomly vared size """
    _color = Color.GREEN()

    def __init__(self, simulation, 
                 int_id : int = DEFAULT_ID,
                 color_gradient : tuple = None,
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
        self.can_think = False

        # initialize the rest of the agar
        Agar.__init__(self, simulation, 
                      int_id = int_id, 
                      size = size, 
                      color_gradient = color_gradient,
                      target_point = position,
                      position = position, 
                      speed = 0, 
                      size_loss_rate = 0, 
                      can_think = False, 
                      can_merge = False,
                      can_split = False,
                      can_eat = False,
                      rect = rect)
        return

    def update_size(self, time_interval : float = 0) -> float:
        # blob size does not change
        return

