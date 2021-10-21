import sys
sys.path.append("..")
from agar import *

class SmartBot(Agar):
    _color = Palette.BLUE
    
    def update_think(self):
        """ Thinking done in the environment """
        pass

    def get_channel_obs(self, n_grid_rows, n_grid_cols, n_channelobs) -> None:
        ''' 
        Stores the observations of each grid square
        obs: np.array(x, y, num_channels) -> The observation at the (x, y) coordinate. 
        The channels observe:
            0 -> Enemy Agars (by their mass size)
            1 -> Blobs (enumerated)
            2 -> Self (mass, ...)
        '''
        obs = np.zeros((n_grid_rows, n_grid_cols, n_channelobs))
        dimensions = obs.shape[:2]
        self.create_grid(dimensions)

        # Check grid for collisions with other agars.
        for i, row in enumerate(self.grid):
            for j, box in enumerate(row):
                # Check for enemies (avg mass).
                obs[i, j, 0] = self.obs_enemy(box)
                # Check for blobs (count)
                obs[i, j, 1] = self.obs_blobs(box)

        # Rescale channels to be [0, 1]
        obs[:, :, 0] /= MAX_AGAR_MASS # Enemies (avg mass)
        obs[:, :, 1] /= 50 # Blobs (enum)
        obs[0, 0, 2] = self.mass / MAX_AGAR_MASS # Agent (mass)

        return obs

    def obs_enemy(self, box):
        total_mass = count = 0
        for agar in self.simulation.agars:
            if (agar != self):
                if (box.colliderect(agar.rect)):
                    # there is an enemy here
                    count += 1
                    total_mass += agar.mass
        return total_mass / count if count else 0

    def obs_blobs(self, box):
        num_blobs_observed = 0
        for blob in self.simulation.blobs:
            if (box.colliderect(blob.rect)):
                # Agent sees number of blobs but not their mass
                num_blobs_observed += 1
        return num_blobs_observed

    def create_grid(self, dimensions):
        """ 
        Creates a grid of box colliders for the agent to observe with.
        Note: dimensions = np.array(rows, columns, number_of_channels)
        """

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
        return self.grid


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


if __name__ == "__main__":
    print("Successfully ran Bots")