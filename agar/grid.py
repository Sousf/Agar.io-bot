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
        self.sub_grids = self.subdivide();
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
                sub_grid = subGrids[i][j];
                print(sub_grid.height, sub_grid.width);
                k += 1;

        print(k);
        return subGrids;


    def add_to_grid(self, agar : Agar):

        posX = agar.position.x;
        posY = agar.position.y;

        i = math.floor(posX / (self.width / self.subdivisions));
        j = math.floor(posY / (self.height / self.subdivisions));

        if (i >= self.subdivisions or j >= self.subdivisions): 
            print(i, j, self.subdivisions);
            return;

        if (agar not in self.sub_grids[i][j].agars):
            self.sub_grids[i][j].agars.append(agar);

        # remove from previous grid
        self.remove_from_grid(agar);
        agar.curr_sub_grid = self.sub_grids[i][j];
        print(agar.curr_sub_grid.id);

        return;

    def remove_from_grid(self, agar):
        if (agar.curr_sub_grid != None and agar in agar.curr_sub_grid.agars):
            agar.curr_sub_grid.agars.remove(agar);
        return;

    # includes the center grid
    def get_adjacent_grids(self, sub_grid):
        j = int(sub_grid.id % self.subdivisions);
        i = int((sub_grid.id - j) / self.subdivisions);
        print(i, j, sub_grid.id);
        adjacent_grids = [];
        for k in range(-1, 2):
            for l in range(-1, 2):
                if (i+k < self.subdivisions and i+k >= 0 and j+l < self.subdivisions and j+l >= 0):
                    adjacent_grids.append(self.sub_grids[i+k][j+l]);
        return adjacent_grids;