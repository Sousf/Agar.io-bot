### LIBRARIES ###
import math;
import random;
import tkinter as gui;
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
k_numAgars = 20;
k_numBlobs = 70;
k_blobSpawnRate = 1.5;
k_frameRate = 0.05;
k_runTime = 30;
k_windowHeight = 720;
k_windowWidth = 1080;

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
        self.window = self.createWindow();
        self.canvas = self.createCanvas(height, width);
        
        # spawns the agars to be used in the simulation
        self.agars = [];
        self.spawnAgars(self.numAgars);
        
        # spawns the initial set of blobs, and then starts spawning blobs every so often
        self.blobs = [];
        self.spawnBlobs(self.numBlobs);

        # begins the simulation
        newFrame = Timer(5, self.drawFrame, args=None, kwargs=None)
        newFrame.start();
        self.window.mainloop();
        return;

    # constructs the window
    def createWindow(self) -> gui.Tk:
        window = gui.Tk();
        return window;

    # constructs the canvas on the window
    def createCanvas(self, _height , _width):
        canvas = gui.Canvas(self.window, width=_width, height=_height, borderwidth=0, highlightthickness=0, bg="#101010");
        canvas.grid();
        canvas.update();
        return canvas;

    # spawns the agars to be used in the simulation
    def spawnAgars(self, numAgars : int = k_numAgars) -> None:
        # itterates through the number of agars to be spawned
        for i in range(numAgars):
            # picks out a position to spawn the agar at
            spawnPos = Vector.withinBounds(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2);
            spawnPos.x += self.canvas.winfo_width() / 2; # centering
            spawnPos.y += self.canvas.winfo_height() / 2; # centering

            # constructs the agar object
            agar = Agar(id = i, position = spawnPos, velocity = Vector(), think = True, canvas = self.canvas);
            # draws it to the canvas
            self.drawAgar(agar);
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
            spawnPos = Vector.withinBounds(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2);
            spawnPos.x += self.canvas.winfo_width() / 2; # centering
            spawnPos.y += self.canvas.winfo_height() / 2; # centering

            # constructs the blob object
            blob = Blob(id = i, position = spawnPos, canvas = self.canvas);
            # draws it to the canvas
            self.drawAgar(blob);
            # appends it to the list of bobs in the simulation
            self.blobs.append(blob);

        # starts a call back for a blob to be spawned at regular intervals
        newBlobSpawn = Timer(self.blobSpawnRate, self.spawnBlobs, args=None, kwargs=None)
        newBlobSpawn.start();
        return None;

    # draws a frame on the interface
    def drawFrame(self) -> None:
        # ends the simulation if it has updated the necessary amount of times
        self.frames += 1;
        if (self.frames * self.frameRate > self.runTime):
            self.endSimulation();
            return;
        # set the positions
        self.updatePositions();
        # check for collisions
        self.checkCollisions();
        # update the canvas
        self.canvas.update();

        # start a callback to update the next frame at the desired frame rate
        newFrame = Timer(self.frameRate, self.drawFrame, args=None, kwargs=None)
        newFrame.start();
        return None;

    # set the agar positions
    def updatePositions(self) -> None:
        for agar in self.agars:
            # update its position based on its velocity
            agar.updatePosition(self.frameRate);
            # check that it is within bounds
            agar.checkBounds(self.canvas);
            # redraw the agar onto the canvas
            self.redrawAgar(agar);
        return None;

    # check for agars that might be colliding
    # will be updated to the chunking method using the grid eventually
    def checkCollisions(self):
        _agars = self.agars;
        for agar in _agars:
            agar.checkCollision(self.agars, self.canvas);
            agar.checkCollision(self.blobs, self.canvas);
        return;

    # redraw an already existing agar
    def redrawAgar(self, agar):
        pos = agar.position;
        rad = agar.size;
        self.canvas.coords(agar.circle, pos.x - rad, pos.y - rad, pos.x + rad, pos.y + rad);
        # self.grid.addToGrid(agar);
        return;

    # draw a new agar
    def drawAgar(self, agar):
        pos = agar.position;
        rad = agar.size;
        agar.circle = self.canvas.create_oval(pos.x - rad, pos.y - rad, pos.x + rad, pos.y + rad, fill = agar.sizeToColor());
        # self.grid.addToGrid(agar);
        return;

    # shut down the simulation
    def endSimulation(self):
        for agar in self.agars:
            agar.think = False;
        self.agars = [];
        self.isRunning = False;
        return;

# Runs a simulation with ~20 'dumb' agar bots
# Extends the base simulation
class DumbSimulation(Simulation):
    def spawnAgars(self, numAgars : int = k_numAgars) -> list:
        for i in range(numAgars):
            spawnPos = Vector.withinBounds(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2);
            spawnPos.x += self.canvas.winfo_width() / 2;
            spawnPos.y += self.canvas.winfo_height() / 2; # centering
            agar = DumbBot(id = i, position = spawnPos, velocity = Vector(), think = True);
            self.drawAgar(agar);
            self.agars.append(agar);
        return None;

# Runs a player controlled agar simulation
# Extends the base simulation
class PlayerSimulation(Simulation):
    def spawnAgars(self, numAgars : int = k_numAgars) -> list:
        spawnPos = Vector(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2);
        agar = Player(id = 0, position = spawnPos, velocity = Vector(), think = True, thinkInterval = self.frameRate, canvas = self.canvas, window = self.window);
        self.drawAgar(agar);
        self.agars.append(agar);
        return None;

# Runs a player controlled agar simulation with a few 'dumb' bots
# Extends the base simulation
class PlayerAndBotSimulation(Simulation):
    def spawnAgars(self, numAgars : int = k_numAgars) -> list:
        spawnPos = Vector(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2);
        agar = Player(id = 0, size = 200, position = spawnPos, velocity = Vector(), think = True, thinkInterval = self.frameRate, window = self.window, canvas = self.canvas);
        self.drawAgar(_agar);
        self.agars.append(_agar);
        for i in range(1, numAgars + 1):
            spawnPos = Vector.withinBounds(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2);
            spawnPos.x += self.canvas.winfo_width() / 2;
            spawnPos.y += self.canvas.winfo_height() / 2; # centering
            agar = DumbBot(id = i, position = spawnPos, velocity = Vector(), think = True, canvas = self.canvas);
            self.drawAgar(agar);
            self.agars.append(agar);
        return None;