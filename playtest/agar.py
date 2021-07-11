### LIBRARIES ###
import time;
import math;
import random;
import tkinter as gui;
from threading import Timer;

### LOCAL MODULES ###
from vectors import Vector;

### MAGIC VARIABLES ###
# default agar parameters (used if not specified at initialisation)
k_minAgarSize = 20;
k_maxAgarSize = 300;
k_agarInitPosition = Vector(0, 0);
k_agarInitVelocity = Vector(0, 0);
k_baseSpeed = 2000;
k_numAgars = 0; # not working (need increment to increment the global variable inside initialization)
k_agarThinkInterval = 1;
# default blob parameters (used if not specified at initialisation)
k_blobMinSize = 6;
k_blobMaxSize = 15;

# The base agar object
# Requires an id (currently useless), size, position, velocity
# Base speed is required to figure out how to scale slowness with size
# Think controls whether it can act (if false, the agar won't be able to do anything)
class Agar():
    def __init__(self, id : int = k_numAgars,  size : float = k_minAgarSize, 
                 position : Vector = k_agarInitPosition, velocity : Vector = k_agarInitVelocity, baseSpeed : float = k_baseSpeed,
                 think : bool = True, thinkInterval : float = k_agarThinkInterval, canvas = None) -> None:

        # basic parameters
        self.id = id;
        self.size = size;
        self.position = position;
        self.velocity = velocity;
        self.baseSpeed = baseSpeed;
        self.canvas = canvas; # the canvas its drawn on

        # start the thinker
        self.thinkInterval = thinkInterval;
        self.startThinker(think);

        # stores the subquadrant that the agar is located in for optimization purposes
        # not used currently, but will be!
        self.currSubGrid = None;
        self.isEaten = False;

        return None;

    # starts the thinker, or stops it
    def startThinker(self, think : bool) -> None:
        # set the state of thinking
        self.think = think;
        # launch the thinkers if necessary
        if (self.think): 
            self.onThink();
        return None;
    
    # the actions to decide every time the agar thinks
    def onThink(self) -> None:
        # shut down the thinker 
        if (self.think == False): return; 

        # update the velocity (i.e choose a direction)
        self.updateVelocity();

        # decide whether to split
        # ///////////////////////

        # start a callback for the next think to occur after an interval
        newThinker = Timer(self.thinkInterval, self.onThink, args=None, kwargs=None)
        newThinker.start();
        return None;

    # update the position based on the velocity and time passed since the last update
    def updatePosition(self, timeInterval : float = 0):
        deltaPosition = self.velocity.scale(timeInterval);
        self.position = self.position.add(deltaPosition);
        return;

    # check that the agar does not go out of bounds
    def checkBounds(self, canvas):
        if (self.position.x >= canvas.winfo_width()):
            self.position.x = canvas.winfo_width();
        elif (self.position.x <= 0):
            self.position.x = 0;
        if (self.position.y >= canvas.winfo_height()):
            self.position.y = canvas.winfo_height();
        elif (self.position.y <= 0):
            self.position.y = 0;
        return;

    # update the velocity (decision dependent on the type of agar)
    def updateVelocity(self, speed):
        # handled in extensions
        return;

    # conversion between the size of the agar and its speed
    def sizeToSpeed(self) -> float:
        return self.baseSpeed / math.sqrt(self.size);

    # conversion between the size of the agar and its color
    def sizeToColor(self):
        sizeRatio = (self.size) / (k_maxAgarSize);
        color = '#%02x%02x%02x' % (int(sizeRatio * 64 + 192), int(sizeRatio * 192 + 64), 0);
        return color;

    # check for collisions
    def checkCollision(self, agars, canvas):
        for agar in agars:
            # collide if within a certain distance
            if (agar != self and Vector.distance(self.position, agar.position) <= self.size + agar.size):
                self.collide(agar, agars, canvas);     
        return;

    # check for collisions
    def collide(self, agar, agars, canvas):
        if (self.size > agar.size):
            self.eat(agar, agars, canvas);
        return;

    def eat(self, agar, agars, canvas):
        self.size = self.size + agar.size / 10;
        agars.remove(agar);
        agar.think = False;
        if (canvas != None): canvas.delete(agar.circle);
        return;
   
# A player controlled agar
# Extends from the base agar
# Requires, additionally, the window that the simulation is being run on
class Player(Agar):
    def __init__(self, id : int = k_numAgars,  size : float = k_minAgarSize, 
                 position : Vector = k_agarInitPosition, velocity : Vector = k_agarInitVelocity, baseSpeed : float = k_baseSpeed,
                 think : bool = True, thinkInterval : float = k_agarThinkInterval,
                 canvas = None, window : gui.Tk = None) -> None:

        # the gui that the player interacts with the agar through
        self.window = window;

        # initalizes the rest of the agar
        Agar.__init__(self, id, size, position, velocity, baseSpeed, think, thinkInterval, canvas);
        return None;

    # update the velocity of the agar to be towards the mouse of the player
    def updateVelocity(self) -> None:
        # cannot calculate mouse position without a window
        if (self.window == None): return;

        # get the appropriate mouse coordinates
        abs_coord_x = self.canvas.winfo_pointerx() - self.window.winfo_rootx()
        abs_coord_y = self.canvas.winfo_pointery() - self.window.winfo_rooty()

        # get the direction between the agar and the mouse
        x = -(self.position.x - abs_coord_x);
        y = -(self.position.y - abs_coord_y);
        direction = Vector(x, y);

        # check that the mouse is far enough away to warrant movement
        if (direction.magnitude() <= 20):
            self.velocity = Vector();
        else:
            self.velocity = direction.mapPosOnUnitCircle().scale(self.sizeToSpeed());
        return None;

# A 'Dumb' Agar bot that randomly picks a direction to move in
# Extends from the base agar
class DumbBot(Agar):

    # randomly select a direction to move in
    def updateVelocity(self):
        self.velocity = Vector.randomPosOnUnitCircle().scale(self.sizeToSpeed());
        return;

# The 'Blob' Agars scattered around the map that stay still and exist only to be eaten
# Extends from the base agar
# Randomly vary their size
class Blob(Agar):
    def __init__(self, id : int = k_numAgars, 
                 minSize : float = k_blobMinSize, maxSize : float = k_blobMaxSize,
                 position : Vector = k_agarInitPosition, canvas = None) -> None:

        # randomly generate the size of the blob
        self.minSize = minSize;
        self.maxSize = maxSize;
        size = random.random() * (maxSize - minSize) + minSize;

        # make sure this isn't thinking (otherwise it would be very heavy)
        self.think = False;

        # initialize the rest of the agar
        Agar.__init__(self, id, size, position, Vector(), 0, False, 1000, canvas = canvas);
        return None;

    # override the coloring of this agar to distinguish it
    def sizeToColor(self):
        sizeRatio = (self.size - self.minSize) / (self.maxSize - self.minSize);
        color = '#%02x%02x%02x' % (int(sizeRatio * 192 + 64), int(sizeRatio * 64 + 192), 0);
        return color;

