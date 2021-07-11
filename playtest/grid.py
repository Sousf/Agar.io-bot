### LIBRARIES ###
import numpy as np;
import math;

### LOCAL MODULES ###
from agar import Agar;

# Generates a chunkable grid to track collisions
# This is causing issues currently
class Grid():
    def __init__(self, id, width : float, height : float, subdivisions : int = 4):
        self.id = id;
        self.width = width;
        self.height = height;
        self.subdivisions = subdivisions;
        self.subGrids = self.subdivide();
        self.agars = [];

    def subdivide(self):
        if (self.subdivisions == 0): return;
        subGrids = np.empty([self.subdivisions, self.subdivisions], dtype=object);
        for i in range(self.subdivisions):
            for j in range(self.subdivisions):
                id = i * self.subdivisions + j;
                width = int(math.floor(self.width / self.subdivisions));
                height = int(math.floor(self.height / self.subdivisions))
                subGrids[i][j] = Grid(id, width, height, 0);
        k = 0;
        for i in range(self.subdivisions):
            for j in range(self.subdivisions):
                subGrid = subGrids[i][j];
                print(subGrid.height, subGrid.width);
                k += 1;

        print(k);
        return subGrids;


    def addToGrid(self, agar : Agar):

        posX = agar.position.x;
        posY = agar.position.y;

        i = math.floor(posX / (self.width / self.subdivisions));
        j = math.floor(posY / (self.height / self.subdivisions));

        if (i >= self.subdivisions or j >= self.subdivisions): 
            print(i, j, self.subdivisions);
            return;

        if (agar not in self.subGrids[i][j].agars):
            self.subGrids[i][j].agars.append(agar);

        # remove from previous grid
        self.removeFromCurrGrid(agar);
        agar.currSubGrid = self.subGrids[i][j];
        print(agar.currSubGrid.id);

        return;

    def removeFromCurrGrid(self, agar):
        if (agar.currSubGrid != None and agar in agar.currSubGrid.agars):
            agar.currSubGrid.agars.remove(agar);
        return;

    # includes the center grid
    def getAdjacentSubGrids(self, subGrid):
        j = int(subGrid.id % self.subdivisions);
        i = int((subGrid.id - j) / self.subdivisions);
        print(i, j, subGrid.id);
        adjacentGrids = [];
        for k in range(-1, 2):
            for l in range(-1, 2):
                if (i+k < self.subdivisions and i+k >= 0 and j+l < self.subdivisions and j+l >= 0):
                    adjacentGrids.append(self.subGrids[i+k][j+l]);
        return adjacentGrids;