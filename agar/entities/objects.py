import sys
sys.path.append("..")
from agar import *

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

if __name__ == "__main__":
    print("Successfully ran Objects")
