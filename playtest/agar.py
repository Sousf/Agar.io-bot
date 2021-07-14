### LIBRARIES ###
import time;
import math;
import random;
import tkinter as gui;
from threading import Timer;
import pygame as game;

### LOCAL MODULES ###
from vectors import Vector;

### MAGIC VARIABLES ###
# default agar parameters (used if not specified at initialisation)
k_minAgarSize = 20;
k_maxAgarSize = 100;
k_agarInitPosition = Vector(0, 0);
k_agarInitVelocity = Vector(0, 0);
# some parameters for controlling stat changes
k_baseSpeed = 500;
k_splitSpeed = 800;
k_maxSpeed = 600;
k_baseSizeLossRate = 0.01; # lose a 100th of your size per second
k_numAgars = 0; # not working (need increment to increment the global variable inside initialization)
k_agarThinkInterval = 1;
# default blob parameters (used if not specified at initialisation)
k_blobMinSize = 6;
k_blobMaxSize = 15;
# time controls for the game, note that these time controls will have to be
# modified into a frame time base to be able to simulate at
# faster the real time speeds
k_splitChildThinkerDelay = 0.75;
k_baseMergeBuffer = 0.75;
k_splitBuffer = 0.3;

# The base agar object
# Requires an id (for splitting and merging), size, position, velocity
# Base speed is required to figure out how to scale slowness with size
# Think controls whether it can act (if false, the agar won't be able to do anything)
class Agar():
    def __init__(self, simulation, id = k_numAgars,  size : float = k_minAgarSize, 
                 position : Vector = k_agarInitPosition, velocity : Vector = k_agarInitVelocity, 
                 baseSpeed : float = k_baseSpeed, baseSizeLossRate : float = k_baseSizeLossRate,
                 think : bool = True, thinkInterval : float = k_agarThinkInterval,
                 canSplit : bool = True, canMerge : bool = True,
                 rect : game.Rect = None) -> None:

        # the parent simulation
        self.simulation = simulation;

        # set the id of the agar
        if (type(id) == str):
            self.id = id;
        else:
            self.id = self.getType() + str(id);
        # basic parameters
        self.size = size;
        self.position = position;
        self.deltaPosition = Vector();
        self.velocity = velocity;
        self.baseSpeed = baseSpeed;
        self.baseSizeLossRate = baseSizeLossRate;
        self.rect = rect; # the canvas its drawn on

        # stores the subquadrant that the agar is located in for optimization purposes
        # not used currently, but will be!
        self.currSubGrid = None;
        self.canSplit = canSplit;
        self.canMerge = canMerge;
        self.isEaten = False;

        # start the thinker
        self.thinkInterval = thinkInterval;
        self.startThinker(think);

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
        self.decideSplit();

        # start a callback for the next think to occur after an interval
        newThinker = Timer(self.thinkInterval, self.onThink, args=None, kwargs=None)
        newThinker.start();
        return None;

    # update the position based on the velocity and time passed since the last update
    def updatePosition(self, timeInterval : float = 0):
        self.deltaPosition = self.velocity.scale(timeInterval);
        self.position = self.position.add(self.deltaPosition);
        return;

    # check that the agar does not go out of bounds
    def checkBounds(self, dimensions):
        if (self.position.x >= dimensions[0]):
            self.position.x = dimensions[0];
        elif (self.position.x <= 0):
            self.position.x = 0;
        if (self.position.y >= dimensions[1]):
            self.position.y = dimensions[1];
        elif (self.position.y <= 0):
            self.position.y = 0;
        return;

    # update the velocity (decision dependent on the type of agar)
    def updateVelocity(self):
        # handled in extensions
        return;

    def updateSize(self, timeInterval : float = 0):
        self.size = self.size - (self.size * self.baseSizeLossRate * timeInterval);
        # overrides the split buffer :(
        # if (self.size > k_minSplitThreshold):
        #    self.canSplit;
        return;

    def decideSplit(self):
        # handled in extensions
        return;

    # conversion between the size of the agar and its speed
    def sizeToSpeed(self) -> float:
        return min(k_maxSpeed, self.baseSpeed / math.sqrt(self.size / k_minAgarSize));

    # conversion between the size of the agar and its color
    def sizeToColor(self):
        sizeRatio = min((self.size) / (k_maxAgarSize), 0.95);
        color = '#%02x%02x%02x' % (int(sizeRatio * 64 + 192), int(sizeRatio * 192 + 64), 0);
        return color;

    # check for collisions
    def onCollision(self, agar):
        if (self == agar): return;
        if (self.id == agar.id): # add the time constraints for merging back together
            self.merge(agar);
        elif (self.size > agar.size):
            self.eat(agar);
        return;

    def eat(self, agar):
        self.size = self.size + agar.size / 5;
        agar.think = False;
        agar.isEaten = True;
        del agar.rect;
        return;

    def split(self):
        if (self.canSplit == False): return;
        # constructs the agar object
        agar = self.clone()
        agar.velocity = agar.velocity.mapPosOnUnitCircle().scale(k_splitSpeed);
        agar.size *= 0.5;
        self.size *= 0.5;
        self.canSplit = False;

        # delay control over the split
        delayedThinker = Timer(k_splitChildThinkerDelay, agar.kickStartThinker, args=None, kwargs=None);
        # delay the abilitiy for the child agar to merge back
        mergeBuffer = Timer(k_baseMergeBuffer, agar.resetMerge, args=None, kwargs=None);
        # delay the ability of the parent agar to split? not sure if this is necessary if there is a size cap
        splitBuffer = Timer(k_splitBuffer, self.resetSplit, args=None, kwargs=None);

        delayedThinker.start();
        mergeBuffer.start();
        splitBuffer.start();

        # appends it to the list of agars in the simulation (not workin)
        # i'd also like to not have to point to the simulation in the agars :(
        agar.rect = self.simulation.renderer.drawAgar(agar);
        self.simulation.agars.append(agar);     
        return;

    def clone(self):
        return Agar(self.simulation, id = self.id, size = self.size, position = self.position, velocity = self.velocity, think = False, canSplit = False, canMerge = False);

    # essentially the same as merging but
    # gain all the size instead of just a portion
    # and snap to the mid point
    def merge(self, agar):
        if (agar.canMerge == False or self.canMerge == False): return; # can't merge until it's buffer is over
        self.size = self.size + agar.size;
        #self.position = Vector.midPoint(self.position, agar.position);
        agar.think = False;
        agar.isEaten = True;
        del agar.rect;
        return;

    def kickStartThinker(self):
        self.startThinker(True);
        return;

    def resetMerge(self):
        self.canMerge = True;
        return;

    def resetSplit(self):
        self.canSplit = True;
        return;

    def getType(self):
        return "base";
   
# A player controlled agar
# Extends from the base agar
# Requires, additionally, the window that the simulation is being run on
class Player(Agar):

    # update the velocity of the agar to be towards the mouse of the player
    def updateVelocity(self) -> None:
        # cannot calculate mouse position without a window
        # if (self.window == None): return;

        # get the appropriate mouse coordinates
        mousePos = game.mouse.get_pos();
        if (self.simulation.renderer.focus != None):
            focusPoint = self.simulation.renderer.focus.position;
        else:
            focusPoint = Vector();
        absX = mousePos[0];
        absY = mousePos[1];

        # get the direction between the agar and the mouse for an unfocused player
        x = (absX - self.simulation.renderer.center.x) - (self.position.x - focusPoint.x);
        y = (absY - self.simulation.renderer.center.y) - (self.position.y - focusPoint.y);
        
        direction = Vector(x, y);

        # check that the mouse is far enough away to warrant movement
        if (direction.magnitude() <= 20):
            self.velocity = Vector();
        else:
            self.velocity = direction.mapPosOnUnitCircle().scale(self.sizeToSpeed());
        return None;

    def decideSplit(self):
        pressedKeys = game.key.get_pressed()
        for keyConstant, pressed in enumerate(pressedKeys): 
            if pressed:
                #keyName = pygame.key.name(keyConstant);
                print("Key Was Pressed");
                self.split();
        return;

    def clone(self):
        # constructs the agar object
        return Player(self.simulation, id = self.id, size = self.size, position = self.position, velocity = self.velocity, think = False, thinkInterval = self.thinkInterval, canSplit = False, canMerge = False);
        
    def getType(self):
        return "player";

# A 'Dumb' Agar bot that randomly picks a direction to move in
# Extends from the base agar
class DumbBot(Agar):

    # randomly select a direction to move in
    # when they split, both agars need to be moving towards a certain point
    # the agars that have the same parent need to be able to communicate with each other (?)
    # right now the child agars move independently of the parent which is incorrect
    def updateVelocity(self):
        self.velocity = Vector.randomPosOnUnitCircle().scale(self.sizeToSpeed());
        return;

    def decideSplit(self):
        if (random.random() > 0.95):
            self.split();
        return;

    def clone(self):
        # constructs the agar object
        return DumbBot(self.simulation, id = self.id, size = self.size, position = self.position, velocity = self.velocity, think = False, thinkInterval = self.thinkInterval, canSplit = False, canMerge = False);
         
    def getType(self):
        return "dumbbot";

# The 'Blob' Agars scattered around the map that stay still and exist only to be eaten
# Extends from the base agar
# Randomly vary their size
class Blob(Agar):
    def __init__(self, simulation, id : int = k_numAgars, 
                 minSize : float = k_blobMinSize, maxSize : float = k_blobMaxSize,
                 position : Vector = k_agarInitPosition, rect : game.Rect = None) -> None:

        # randomly generate the size of the blob
        self.minSize = minSize;
        self.maxSize = maxSize;
        size = random.random() * (maxSize - minSize) + minSize;

        # make sure this isn't thinking (otherwise it would be very heavy)
        self.think = False;

        # initialize the rest of the agar
        Agar.__init__(self, simulation, id, size, position, Vector(), 0, 0, False, 1000, rect = rect);
        return None;

    # override the coloring of this agar to distinguish it
    def sizeToColor(self):
        sizeRatio = (self.size - self.minSize) / (self.maxSize - self.minSize);
        color = '#%02x%02x%02x' % (int(sizeRatio * 192 + 64), int(sizeRatio * 64 + 192), 0);
        return color;

    def clone(self):
        return self;

    def getType(self):
        return "blob";

