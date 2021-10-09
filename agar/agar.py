""" IMPORTED LIBRARIES """
import time
import math
import random
import tkinter as gui
from threading import Timer
import pygame as game
from dataclasses import dataclass
import numpy as np

""" LOCAL MODULES """
from vectors import Vector
from color import Palette
from debug import Debug

""" GLOBAL VARIABLES """
# default agar parameters (used if not specified at initialisation)
DEFAULT_ID = 0

# vectors
DEFAULT_AGAR_POSITION = Vector(0, 0)
DEFAULT_AGAR_VELOCITY = Vector(0, 0)
EJECTED_AGAR_SHAKE_ANGLE = 30

# controls the speed
ACCELERATION = 3000
MAX_CURSOR_RANGE = 300
BASE_SPEED = 750
SPLIT_SPEED = 1500
EJECT_SPEED = 2000
MAX_SPEED = 600

# controls the size for agars
MIN_AGAR_MASS = 20
MAX_AGAR_MASS = 2000

BASE_MASS_LOSS_RATE = 0.02 # lose a 50th of your size per second
MASS_TO_SIZE_EXPONENT = 0.75 # realistically this should be 0.5
MASS_SPEED_FACTOR = 1.25 # should be 1.44?

EAT_SIZE_THRESHOLD = 1.05 # should be 1.25
EAT_MASS_GAIN_FACTOR = 1 # the percentage of mass gained when eating

EJECTED_MASS_FACTOR = 0.18
EJECTED_MASS_LOSS = 0.75 # 0.72

VIRUS_BASE_MASS = 100
VIRUS_EAT_THRESHOLD = 150 # 133 in real game
VIRUS_POP_NUMBER = 7

# controls the size for blobs
MIN_BLOB_MASS = 1
MAX_BLOB_MASS = 1
BLOB_COLORS = [(255, 0, 0), (255)]

# all time controls relative to a frame rate of 60

# time controls for the merging
BASE_MERGE_DELAY = 10 # should be 30 for irl agar io
MERGE_DELAY_FACTOR = 0.0233

# time controls for the splitting
SPLIT_CHILD_THINKER_DELAY = 0.2
DEFAULT_SPLIT_DELAY = 0.3

# time controls for ejection
DEFAULT_EJECT_DELAY = 0.2
EJECT_CHILD_DISTANCE = 1250

""" AGAR OBJECT """
class Agar():
    """ 
    Requires an id (for splitting and merging), size, position, velocity
    Base speed is required to figure out how to scale slowness with size
    Think controls whether it can act (if false, the agar won't be able to do anything)
    """
    _color = Palette.GREY
    def __init__(self, simulation, 
                 int_id = DEFAULT_ID,
                 mass : float = MIN_AGAR_MASS,
                 size_loss_rate : float = BASE_MASS_LOSS_RATE,
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
        self.mass = mass
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
        self.children = []

        # states
        self.is_eaten = is_eaten

        # delays
        self.delayed_think = False
        self.delayed_merge = False
        self.delayed_split = False
        self.delayed_eject = False

        self.grid = None

        return

    """ UPDATES """
    # the actions to decide every time the agar thinks
    def update_think(self) -> bool:
        # don't think if it can't or is not the parent
        if (self.can_think == False or self.parent != None): 
            return False

        # decide a direction to travel in
        self.decide_target_point()
        # decide whether to split
        # split = self.decide_to_split()
        # decide whether to eject
        # eject = self.decide_to_eject()

        # itterate through the children
        # for child in self.children:
        #   if (child.can_think):
        #        child.target_point = self.target_point
        #        if (split):
        #            child.split()
        #        if (eject):
        #            child.eject()

        return True

    # update the velocity based on the acceleration and time passed since the last update
    def update_velocity(self, time_interval : float = 0) -> Vector:
        # snap this for cohesion
        if ((self.target_velocity - self.velocity).magnitude() < time_interval * ACCELERATION):
            self.delta_velocity = Vector()
            self.velocity = self.target_velocity
        else:
            self.delta_velocity = (self.target_velocity - self.velocity).normalize() * time_interval * ACCELERATION
            self.velocity = self.velocity + self.delta_velocity
        # self.velocity = self.target_velocity
        return self.velocity

    # update the position based on the velocity and time passed since the last update
    def update_position(self, time_interval : float = 0) -> Vector:
        self.delta_position = self.velocity * time_interval
        self.position = self.position + self.delta_position
        return self.position

    # update the size lost based on time passed since last update
    def update_size(self, time_interval : float = 0) -> float:
        self.mass = max(MIN_AGAR_MASS, self.mass - (self.mass * self.size_loss_rate * time_interval))
        self.mass = min(MAX_AGAR_MASS, self.mass)
        # check whether the agar is over the splitting/ejecting threshold
        return self.mass

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
        self.check_split()
        if (self.can_split == False): return
        Debug.agar(self.id + " is splitting")

        # splits the agar
        clone = self.split_clone()   
        self.can_split = False

        # slight delay before gaining control
        clone.delayed_think = self.simulation.create_timer(time_interval = SPLIT_CHILD_THINKER_DELAY, method = clone.enable_think)
        
        # delay before this can merge back to the parent
        clone.delayed_merge = self.simulation.create_timer(time_interval = clone.merge_cooldown, method = clone.enable_merge)
        
        # delay before these can split again
        clone.delayed_split = self.simulation.create_timer(time_interval = DEFAULT_SPLIT_DELAY, method = clone.enable_split)
        self.delayed_split = self.simulation.create_timer(time_interval = DEFAULT_SPLIT_DELAY, method = self.enable_split)

        # appends it to the list of agars in the simulation
        if (self.parent == None):
            self.children.append(clone)
        else:
            self.parent.children.append(clone)
        self.simulation.agars.append(clone)     
        return

        # run through the process for splitting mechanic
    def no_delay_split(self):
        self.check_split()
        if (self.can_split == False): return None
        Debug.agar(self.id + " is splitting")

        # splits the agar
        clone = self.no_delay_split_clone()   
        self.can_split = False

        # slight delay before gaining control
        clone.delayed_think = self.simulation.create_timer(time_interval = SPLIT_CHILD_THINKER_DELAY, method = clone.enable_think)
        
        # delay before this can merge back to the parent
        clone.delayed_merge = self.simulation.create_timer(time_interval = clone.merge_cooldown, method = clone.enable_merge)
        
        # delay before these can split again
        clone.can_split = True
        self.can_split = True

        # appends it to the list of agars in the simulation
        if (self.parent == None):
            self.children.append(clone)
        else:
            self.parent.children.append(clone)
        self.simulation.agars.append(clone)     
        return clone

    def eject(self) -> None:
        self.check_eject()
        if (self.can_eject == False): return
        Debug.agar(self.id + " is ejecting")

        # constructs the agar object
        clone = self.eject_clone()  
        self.can_eject = False

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
                    mass = self.mass,
                    color_gradient = self.color_gradient,
                    target_point = self.position + self.target_point.normalize() * EJECT_CHILD_DISTANCE,
                    position = self.position,
                    speed = self._speed,
                    can_think = True, 
                    can_split = False, 
                    can_merge = False,
                    parent = self
                    )
        # get the upper most parent
        if (self.parent != None):
            clone.parent = self.parent
        clone.velocity = self.target_velocity.normalize() * SPLIT_SPEED # no acceleration on start up
        clone.mass *= 0.5
        self.mass *= 0.5
        clone.position = self.position + (self.target_velocity.normalize() * (self.size + clone.size + 10))
        return clone

    # clones the object at half size
    def no_delay_split_clone(self):
        clone = type(self)(self.simulation, 
                    int_id = self.int_id, 
                    mass = self.mass,
                    color_gradient = self.color_gradient,
                    target_point = self.target_point,
                    position = self.position,
                    speed = self._speed,
                    can_think = False, 
                    can_split = False, 
                    can_merge = False,
                    parent = self
                    )
        # get the upper most parent
        if (self.parent != None):
            clone.parent = self.parent
        clone.velocity = Vector(1, 0).shake(360).normalize() * SPLIT_SPEED # no acceleration on start up
        clone.mass *= 0.5
        self.mass *= 0.5
        clone.position = self.position + (self.target_velocity.normalize() * (self.size + clone.size + 10))
        return clone

    # clones the object as a blob with a fraction of the size
    def eject_clone(self):
        clone = Blob(self.simulation, 
                     int_id = self.int_id, 
                     min_mass = self.mass, max_mass = self.mass + 1,
                     color_gradient = self.color_gradient,
                     position =  self.position)
        clone.can_think = False
        clone.target_point = self.target_point
        clone.velocity = self.target_velocity.normalize() * EJECT_SPEED
        clone.mass = self.mass * EJECTED_MASS_FACTOR
        self.mass = self.mass * (1 - EJECTED_MASS_FACTOR) * EJECTED_MASS_LOSS
        clone.position = self.position + (self.target_velocity.normalize() * (self.size + clone.size + 10))
        return clone

    """ COLLISIONS """
    # check for collisions
    def on_collision(self, agar) -> None:
        # cannot collide with self
        if (self.can_eat == False or self == agar): 
            return

        # can always eat blobs
        if (type(agar) == Blob):
            if (self.encompasses(agar)):
                self.eat(agar)
                return
        # viruses can't do anything beyond this point (only eat blobs)
        if (type(self) == Virus):
            return
        # on the other hand, if we hit a virus
        elif (type(agar) == Virus):
            if (self.mass > VIRUS_EAT_THRESHOLD and self.encompasses(agar)):
                # eat the virus then pop the cell upto 16 pieces
                self.eat_virus(agar)
            else:
                # hide the cell
                pass
        # for collisions between the same agar we merge
        elif (self.id == agar.id):
            if (self.parent == None and self.can_merge == True and agar.can_merge == True):
                self.merge(agar)
            elif (self.mass >= agar.mass):
                self.boundary(agar)
            # else:
            #   agar.boundary(self)
        # for collisions between different agars attempt to eat
        elif (self.mass >= EAT_SIZE_THRESHOLD * agar.mass):
            if (self.encompasses(agar)):
                self.eat(agar)
        # so that boundary is not affected when they try to eat you
        elif (agar.mass < EAT_SIZE_THRESHOLD * self.mass):
            self.boundary(agar)
        return

    # check if an agar encompasses a certain point
    def encompasses(self, agar : tuple) -> bool:
        #return self.rect.collidepoint(agar.rect.center)
        if (Vector.distance(self.position, agar.position) <= self.size):
            return True
        return False

    def eat_virus(self, agar):

        self.eat(agar)

        split_these = [self]
        _split_these = [self]
        for i in range(4):
            for member in split_these:
                clone = member.no_delay_split()
                if (clone != None):
                    _split_these.append(clone)
            split_these = _split_these
        self.simulation.renderer.render_frame()

        return

    # run through the process for eating another agar
    def eat(self, agar) -> None:
        Debug.agar(self.id + " eats " + agar.id + ", gaining {0:.2f} size".format(agar.mass / 5))
        self.mass = self.mass + agar.mass / EAT_MASS_GAIN_FACTOR

        if (len(agar.children) > 0):
            new_parent = agar.children[0]
            new_parent.children = agar.children[1:]
            for child in new_parent.children:
                child.parent = new_parent
            new_parent.parent = None
            if (self.simulation.renderer.focus == agar):
                self.simulation.renderer.focus = new_parent
            
        agar.disable()
        return

    # run through the process of merging with another agar
    def merge(self, agar) -> None:
        Debug.agar(self.id + " merges  back, gaining {0:.2f} size".format(agar.mass))
        self.mass = self.mass + agar.mass

        if (agar in self.children):
            self.children.remove(agar)

        agar.disable()
        return

    def boundary(self, agar) -> None:
        if (0 < Vector.distance(self.position, agar.position) <= self.size + agar.size):
            # push it out a little
            # = 1 at contact
            #dist_normalized = max(0.5, Vector.distance(self.position, agar.position) / (self.size + agar.size))
            #direction = (self.position - agar.position).normalize()
            #projection = agar.velocity.dot(direction) * 1.1
            # need to do some projection here(?) idea seems to work but numbers are too high
            # agar.velocity = agar.velocity -  direction * (projection / dist_normalized )
            perimeter = (agar.position - self.position).normalize() * (self.size + agar.size)
            agar.position = self.position + perimeter
        return

    """ SWITCHES """
    # disable the whole agar
    def disable(self) -> None:

        # remove times

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
        self.delayed_merge = False
        return

    # splitting
    def check_split(self):
        if (self.delayed_split == False):
            if (self.parent == None):
                if (len(self.children) >= 15):
                    self.can_split = False
                    return
            elif (len(self.parent.children) >= 15):
                self.can_split = False
                return
            if (self.mass < 2 * MIN_AGAR_MASS):
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
            if (self.mass < 2 * MIN_AGAR_MASS):
               self.can_eject = False
            else:
                self.can_eject = True
        return

    def enable_eject(self):
        self.can_eject = True
        self.delayed_eject = False
        return


    """ CONVERSIONS """
    @property
    def size(self):
        return MIN_AGAR_MASS * math.pow(self.mass / MIN_AGAR_MASS, MASS_TO_SIZE_EXPONENT)

    @property
    def target_velocity(self):
        target_direction = self.target_point - self.position
        # snap this for cohesion
        if (target_direction.magnitude() < 20):
            target_velocity = Vector()
        elif (target_direction.magnitude() < MAX_CURSOR_RANGE):
            target_velocity = target_direction.normalize() * self.speed * (target_direction.magnitude() / MAX_CURSOR_RANGE)
        else:
            target_velocity = target_direction.normalize() * self.speed
        return target_velocity

    # conversion between the size of the agar and its speed
    @property
    def speed(self) -> float:
        if (self.can_think == False):
            return self._speed
        mass = self.mass / 10
        return min(MAX_SPEED, self._speed * mass / math.pow(mass, MASS_SPEED_FACTOR))

    # conversion between the size of the agar and its speed
    @property
    def merge_cooldown(self) -> float:
        return BASE_MERGE_DELAY + (MERGE_DELAY_FACTOR * self.mass)

    # conversion that outputs the id
    @property
    def id(self) -> str:
        str_id = type(self).__name__ + str(self.int_id)
        return str_id


class SmartBot(Agar):
    _color = Palette.BLUE
    
    def update_think(self):
        # all thinking done in workspace

        # but need to pass that thinking to children
        """for child in self.children:
            if (child.can_think):
                child.target_point = self.target_point"""

        pass

    def get_channel_obs(self, n_grid_rows, n_grid_cols, n_channelobs) -> None:
        ''' obs: np.array(x, y, num_channels)'''
        obs = np.zeros((n_grid_rows, n_grid_cols, n_channelobs))
        dimensions = obs.shape[:2]
        self.create_grid(dimensions)

        # check grid for collisions with other agars
        for i, row in enumerate(self.grid):
            for j, box in enumerate(row):
                # Check for enemies (avg mass)
                total_mass = count = 0
                for agar in self.simulation.agars:
                    if (agar != self):
                        if (box.colliderect(agar.rect)):
                            # there is an enemy here
                            count += 1
                            total_mass += agar.mass

                obs[i, j, 0] = total_mass / count if count else 0
                        
                # Check for blobs (count)
                for blob in self.simulation.blobs:
                    if (box.colliderect(blob.rect)):
                        # Agent sees number of blobs but not their mass
                        obs[i, j, 1] += 1

        # Rescale channels to be [0, 1]
        # Enemies (/MAX_AGAR_MASS)
        obs[:, :, 0] /= MAX_AGAR_MASS

        # Blobs (/50)
        obs[:, :, 1] /= 50

        # Agent mass
        obs[0, 0, 2] = self.mass / MAX_AGAR_MASS

        return obs

    def create_grid(self, dimensions):

        '''
        dimensions = np.array(x, y, number_of_channels)
            x, y = 2, 4
                □□□□
                □□□□
        '''
        self.grid = []

        box_height = self.simulation.vision_dimensions[1] / dimensions[0]
        box_width  = self.simulation.vision_dimensions[0] / dimensions[1]
        for i in range(dimensions[0]):
            row = []
            for j in range(dimensions[1]):
                rect = game.Rect((j * box_width  + self.position.x - (self.simulation.vision_dimensions[0] / 2), 
                                  i * box_height + self.position.y - (self.simulation.vision_dimensions[1] / 2)), 
                                  (box_width, box_height))
                row.append(rect)
            self.grid.append(row)

        #rect = game.Rect( self.position.x - 300, self.position.y - 300, self.position.x + 300, self.position.y + 300)
        #game.draw.rect(surface = self.simulation.renderer.window, color = self.color_gradient[1],  rect = rect)

        return

class Player(Agar):
    """ A player controlled agar """
    _color = Palette.BLUE

    # update the velocity of the agar to be towards the mouse of the player
    def decide_target_point(self) -> None:
        self.target_point = self.get_mouse_relative_pos()
        return

    # split if the keyboard is pressed
    def decide_to_split(self) -> bool:
        if (self.check_key(game.K_SPACE)):
            self.split()
            return True
        return False

    # split if the keyboard is pressed
    def decide_to_eject(self) -> bool:
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
            mouse_absolute_pos = mouse_vector + self.position - self.simulation.vision_center
        else:
            mouse_absolute_pos = mouse_vector + self.parent.position - self.simulation.vision_center

        return mouse_absolute_pos

class DumbBot(Agar):
    """ A 'Dumb' Agar bot that randomly picks a direction to move in """
    _color = Palette.RED

    # randomly select a direction to move in
    def decide_target_point(self) -> None:
        # when they split, both agars need to be moving towards a certain point
        # the agars that have the same parent need to be able to communicate with each other (?)
        # right now the child agars move independently of the parent which is incorrect
        vision_bounds = self.simulation.vision_dimensions
        if (random.random() > 0.95):
            self.target_point = Vector.random_vector_within_bounds([0, vision_bounds[0]], [0, vision_bounds[1]]) + self.position - self.simulation.vision_center
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
    _color = Palette.GREEN

    def __init__(self, simulation, 
                 int_id : int = DEFAULT_ID,
                 color_gradient : tuple = None,
                 min_mass : float = MIN_BLOB_MASS, 
                 max_mass : float = MAX_BLOB_MASS,
                 position : Vector = DEFAULT_AGAR_POSITION, 
                 rect : game.Rect = None
                 ) -> None:

        # randomly generate the size of the blob
        self.min_mass = min_mass
        self.min_mass = max_mass
        mass = random.random() * (max_mass - min_mass) + min_mass

        # initialize the rest of the agar
        Agar.__init__(self, simulation, 
                      int_id = int_id, 
                      mass = mass, 
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

class Virus(Agar):
    _color = Palette.YELLOW
    def __init__(self, simulation, 
                 int_id = DEFAULT_ID,
                 target_point : Vector = None,
                 position : Vector = DEFAULT_AGAR_POSITION, 
                 rect : game.Rect = None,
                 color_gradient : tuple = None,
                 parent = None,
                 is_eaten : bool = False
                 ) -> None:

        self.num_blobs_eaten = 0
        self.incoming_blob_direction = Vector()
        if (target_point == None):
            target_point = position

        Agar.__init__(self, simulation, 
                      int_id = int_id, 
                      mass = VIRUS_BASE_MASS, 
                      size_loss_rate = 0,
                      color_gradient = color_gradient,
                      target_point = target_point,
                      position = position, 
                      speed = 500, 
                      can_think = True, 
                      can_merge = False,
                      can_split = False,
                      can_eat = True,
                      parent = parent,
                      rect = rect)

        return


    # viruses should only eat blobs
    def eat(self, agar) -> None:
        Debug.agar(self.id + " eats " + agar.id + ", gaining {0:.2f} size".format(agar.mass / 5))
        # self.mass = self.mass + agar.mass / EAT_MASS_GAIN_FACTOR
        if (agar.mass > 5):
            self.num_blobs_eaten += 1
            self.incoming_blob_direction = (self.position - agar.position).normalize()

        agar.disable()
        return

    # split itself if you're too big
    def decide_to_split(self) -> bool:
        if (self.num_blobs_eaten >= VIRUS_POP_NUMBER):
            # target point should be decided by where the blob is coming in from
            self.split()
            return True
        return False

    def split(self) -> None:
        self.check_split()
        if (self.can_split == False): return
        Debug.agar(self.id + " is splitting")

        # splits the agar
        clone = self.split_clone()   
        self.can_split = False

        # slight delay before gaining control
        clone.delayed_think = self.simulation.create_timer(time_interval = SPLIT_CHILD_THINKER_DELAY, method = clone.enable_think)
        
        # delay before this can merge back to the parent
        clone.delayed_merge = False
        
        # delay before these can split again
        clone.delayed_split = self.simulation.create_timer(time_interval = DEFAULT_SPLIT_DELAY, method = clone.enable_split)
        self.delayed_split = self.simulation.create_timer(time_interval = DEFAULT_SPLIT_DELAY, method = self.enable_split)

        # appends it to the list of agars in the simulation
        #self.children.append(clone)
        self.simulation.agars.append(clone)     
        return

    # issues
    def split_clone(self):
        clone = type(self)(self.simulation, 
                    int_id = self.int_id, 
                    target_point = self.incoming_blob_direction * 500 + self.target_point,
                    position = self.position,
                    parent = None
                    )
        # get the upper most parent
        clone.can_think = True
        clone.velocity = clone.target_velocity.normalize() * SPLIT_SPEED # no acceleration on start up
        clone.mass = VIRUS_BASE_MASS
        self.mass = VIRUS_BASE_MASS
        clone.position = self.position + (clone.target_velocity.normalize() * (self.size + clone.size + 10))
        self.num_blobs_eaten = 0
        return clone

    def check_split(self):
        if (self.delayed_split == False):
            if (self.num_blobs_eaten < VIRUS_POP_NUMBER):
                self.can_split = False
            else:
                self.can_split = True
        return


