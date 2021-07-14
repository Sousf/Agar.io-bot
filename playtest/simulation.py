### LIBRARIES ###
import math;
import random;
import tkinter as gui;
import pygame as game;
from threading import Timer;

### LOCAL MODULES ###
from agar import Agar;
from agar import Player;
from agar import DumbBot;
from agar import Blob;
from vectors import Vector;
from grid import Grid;

### MAGIC VARIABLES ###
# default values for simulation (if not specified on initialization)
k_numAgars = 50;
k_numBlobs = 100;
k_blobSpawnRate = 1;
k_frameRate = 1/60;
k_runTime = 15;
k_windowHeight = 1080;
k_windowWidth = 1920;

# The base simulation
# Requires the number of agars, blobs, blob spawn rate, and the window construction params
# Runs for the duration of the run time (note, the run time is calculated on the agar's physics 
# (i.e. it matches the timing that agar's update at so that the simulation completes, 
# regardless of if this matches real time values)
class Simulation():
    def __init__(self, numAgars : int = k_numAgars, 
                 numBlobs : int = k_numBlobs, blobSpawnRate : float = k_blobSpawnRate,
                 height : float = k_windowHeight, width : float = k_windowWidth,
                 frameRate : float = k_frameRate, runTime : float = k_runTime):

        # sets the base parameters
        self.numAgars = numAgars;
        self.numBlobs = numBlobs;
        self.blobSpawnRate = blobSpawnRate
        self.frameRate = frameRate;
        self.frames = 0;
        self.runTime = runTime;
        self.isRunning = True;

        # used for collisions
        # self.grid = Grid(0, width, height, 10);

        # constructs the interface
        self.renderer = Renderer(self);
        
        # spawns the agars to be used in the simulation
        self.agars = [];
        self.spawnAgars(self.numAgars);
        
        # spawns the initial set of blobs, and then starts spawning blobs every so often
        self.blobs = [];
        self.spawnBlobs(self.numBlobs);

        # begins the simulation
        self.start();
        return;   

    # spawns the agars to be used in the simulation
    def spawnAgars(self, numAgars : int = k_numAgars) -> None:
        # itterates through the number of agars to be spawned
        for i in range(numAgars):
            # picks out a position to spawn the agar at
            spawnPos = Vector.withinBounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]));
            # constructs the agar object
            agar = Agar(self, id = i, position = spawnPos, velocity = Vector(), think = True);
            # appends it to the list of agars in the simulation
            self.agars.append(agar);     
        return None; 

    # spawns the blobs used in the simulation, defaults to one blob
    def spawnBlobs(self, numBlobs : int = 1) -> None:
        # don't spawn more blobs if the simulation has ended
        if (self.isRunning == False): return;

        # itterates through the number of blobs to be spawned
        for i in range(numBlobs):
            # picks out a position to spawn the agar at
            spawnPos = Vector.withinBounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]));
            # constructs the blob object
            blob = Blob(self, id = i, position = spawnPos);
            # appends it to the list of bobs in the simulation
            self.blobs.append(blob);

        # starts a call back for a blob to be spawned at regular intervals
        newBlobSpawn = Timer(self.blobSpawnRate, self.spawnBlobs, args=None, kwargs=None)
        newBlobSpawn.start();
        return None;

    # draws a frame on the interface
    def update(self) -> None:
        # ends the simulation if it has updated the necessary amount of times
        self.frames += 1;
        if (self.frames * self.frameRate > self.runTime):
            self.end();
            return;

        # set the positions
        self.updatePositions();
        # set the sizes
        self.updateSizes();
        # update the window
        self.renderer.update();
        # check for collisions
        self.checkCollisions();

        # start a callback to update the next frame at the desired frame rate
        nextUpdate = Timer(self.frameRate, self.update, args=None, kwargs=None)
        nextUpdate.start();
        return None;

    # set the agar positions
    def updatePositions(self) -> None:
        for agar in self.agars:
            # update its position based on its velocity
            agar.updatePosition(self.frameRate);
            # check that it is within bounds
            agar.checkBounds(self.renderer.dimensions);
        return None;

    # set the sizes
    def updateSizes(self) -> None:
        for agar in self.agars:
            agar.updateSize(self.frameRate);
        return None;

    # checks if agars are colliding
    # probs need to optimise this
    def checkCollisions(self) -> None:
        # generate a list of the current active colliders
        activeAgarColliders = self.updateColliders(self.agars);
        activeBlobColliders = self.updateColliders(self.blobs);

        # check for agars colliding with other agars
        # copy list to be able to modify original
        agars = self.agars;
        for agar in agars:
            # check for agars that have been eaten this frame
            # but are still being itterated over
            # as they have not yet been ejected from the list
            if (agar.isEaten == False):
                self.agars, activeAgarColliders = self.checkCollision(agar, self.agars, activeAgarColliders);
                self.blobs, activeBlobColliders = self.checkCollision(agar, self.blobs, activeBlobColliders);                              
        return None;
    
    def checkCollision(self, agar, agars, activeColliders) -> (list, list):
        # returns the indices of the all the collisions found
        collisionIndices = agar.rect.collidelistall(activeColliders);
        for index in collisionIndices:
            # check if the collision results in the agar eating
            agar.onCollision(agars[index]);
            # if the agar has been eaten
            if (agars[index].isEaten):
                # remove the agar collider that was eaten
                # from both lists
                del agars[index];
                del activeColliders[index];
                # we're editing the active collider list here
                # this is going to make the list of collision indices useless
                # as they point to locations within this active collider list
                # breaking here to avoid the issue
                # but this means only one collision that results in eating can be detected per frame
                # im sure there is a more elegant solution
                return (agars, activeColliders);
        return (agars, activeColliders);


    def updateColliders(self, agars) -> list:
        activeColliders = [];
        for agar in agars:
            if (agar.rect != None):
                activeColliders.append(agar.rect);
        return activeColliders;

    # start the simulation
    def start(self):
        self.renderer.start();
 
        # begins the simulation
        nextUpdate = Timer(2, self.update, args=None, kwargs=None)
        nextUpdate.start();
        return;

    # shut down the simulation
    def end(self):
        for agar in self.agars:
            agar.think = False;
        self.agars = [];
        self.isRunning = False;

        # closes the window after a short buffer (not working)
        closeRenderer = Timer(3, self.renderer.close, args=None, kwargs=None)
        closeRenderer.start();
        return;

    def getCaption(self) -> str:
        return "";



# Runs a simulation with ~20 'dumb' agar bots
# Extends the base simulation
class DumbSimulation(Simulation):
    def spawnAgars(self, numAgars : int = k_numAgars) -> list:
        for i in range(numAgars):
            spawnPos = Vector.withinBounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]));
            agar = DumbBot(self, id = i, position = spawnPos, velocity = Vector(), think = True);
            self.agars.append(agar);
        return None;
 
    def getCaption(self) -> str:
        return "DumbSimulation";


# Runs a player controlled agar simulation
# Extends the base simulation
class PlayerSimulation(Simulation):
    def spawnAgars(self, numAgars : int = k_numAgars) -> list:
        spawnPos = Vector(self.renderer.dimensions[0] / 2, self.renderer.dimensions[1] / 2);
        agar = Player(self, id = 0, position = spawnPos, velocity = Vector(), think = True, thinkInterval = self.frameRate);
        self.renderer.setFocus(agar);
        self.agars.append(agar);
        return None;

    def getCaption(self) -> str:
        return "PlayerSimulation";

# Runs a player controlled agar simulation with a few 'dumb' bots
# Extends the base simulation
class PlayerAndBotSimulation(Simulation):
    def spawnAgars(self, numAgars : int = k_numAgars) -> list:
        spawnPos = Vector(self.renderer.dimensions[0] / 2, self.renderer.dimensions[1] / 2);
        agar = Player(self, id = 0, size = 200, position = spawnPos, velocity = Vector(), think = True, thinkInterval = self.frameRate);
        self.agars.append(agar);
        for i in range(1, numAgars + 1):
            spawnPos = Vector.withinBounds((0, self.renderer.dimensions[0]), (0, self.renderer.dimensions[1]));
            agar = DumbBot(self, id = i, position = spawnPos, velocity = Vector(), think = True);
            self.agars.append(agar);
        return None;

    def getCaption(self) -> str:
        return "PlayerAndBotSimulation";

class Renderer():
    def __init__(self, simulation : Simulation, caption : str = "Agar IO", width : float = k_windowWidth,  height : float = k_windowHeight, color : str = '#000000'):      
        
        self.simulation = simulation
        self.dimensions = (width, height);
        self.center = Vector(self.dimensions[0] / 2, self.dimensions[1] / 2);
        self.color = color;

        self.caption = self.simulation.getCaption() or caption;
        game.display.set_caption(self.caption);
        self.window = game.display.set_mode(self.dimensions);
        self.background = game.Surface(self.dimensions)
        self.background.fill(game.Color(self.color))

        self.focus = None;
        return;

    def start(self):
        game.init();
        self.font = game.font.Font('freesansbold.ttf', 15)

        self.open = True;
        for agar in self.simulation.agars:
            agar.rect = self.drawAgar(agar);
        for blob in self.simulation.blobs:
            blob.rect = self.drawAgar(blob);
        game.display.update();
        return;

    def update(self):
        if (self.open == False): return;
        if (self.focus == None):
            origin = Vector();
        else:
            origin = self.focus.position.scale(-1).add(self.center);
        for event in game.event.get():
             if event.type == game.QUIT:
                 self.close();
        self.window.blit(self.background, (0, 0));
        for agar in self.simulation.agars:
            agar.rect = self.drawAgar(agar, origin);
             # change this to display whatever info we want
             # e.g. agar's id, size, number of eaten things, speed, current position etc
            self.addText(agar, str(agar.id));
        for blob in self.simulation.blobs:
            blob.rect = self.drawAgar(blob, origin);
        game.display.update();
        return;

    def close(self) -> None:
        game.display.quit();
        game.quit();
        self.open = False;
        return None;

    def setFocus(self, agar : Agar = None) -> None:
        self.focus = agar;
        return None;

    # draw a new agar
    def drawAgar(self, agar : Agar, origin : Vector = Vector()) -> game.Rect:
        pos = agar.position.add(origin);
        rad = agar.size;
        color = game.Color(agar.sizeToColor());
        return game.draw.circle(self.window, color, (pos.x, pos.y), rad);

    def addText(self, agar, text):
        textSurface, textRect  = self.textObject(text, game.Color("#ffffff"));
        textRect.center=agar.rect.center;
        self.window.blit(textSurface, textRect);
        return

    def textObject(self, text, color):
        textSurface = self.font.render(text, True, game.Color(color));
        return (textSurface, textSurface.get_rect());

if __name__ == "__main__":
    renderer = Renderer();