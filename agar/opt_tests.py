
from numba import jit, njit, vectorize
import numpy
from agar import Agar
import pygame as game
import time
import random
from vectors import Vector

TEST_COUNT = 1000

def setup():
    agars = []
    dimensions = (1000, 1000)
    game.display.set_caption("Testing")
    window = game.display.set_mode(dimensions)
    background = game.Surface(dimensions)
    background_color = (0, 0, 0)
    background.fill(game.Color(background_color))

    for i in range(TEST_COUNT):
        agar = Agar(None, int_id = i, position = Vector(1000 * random.random(), 1000 * random.random()) )
        agar.rect = render_agar(agar, window)
        agars.append(agar)
    return agars

# draw a new agar
def render_agar(agar, window) -> game.Rect:
    rect = game.draw.circle(surface = window, color = game.Color((255, 0, 0)), center = (0, 0), radius = 50)
    return rect

def check_collisions(agars) -> None:
    # generate a list of the current active colliders
    agar_colliders = get_colliders(agars)

    # check for agars colliding with other agars
    # copy list to be able to modify original
    agars = agars
    for agar in agars:
        # check for agars that have been eaten this frame
        # but are still being itterated over
        # as they have not yet been ejected from the list
        if (agar.is_eaten == False):
            agars, agar_colliders = check_collision(agar, agars, agar_colliders)
    return

# check collisions between an agar and a list agars/colliders
def check_collision(agar, agars, colliders):
    # returns the indices of the all the collisions found
    collision_indices = agar.rect.collidelistall(colliders)

    # runs through all the collisions
    #for index in collision_indices:
    #    agar.on_collision(agars[index])
    #    if (agars[index].is_eaten):
    #        # remove the agar collider that was eaten from both lists if it was eaten
    #        del agars[index]
    #        del colliders[index]
    #        """
    #        we're editing the active collider list here
    #        this is going to make the list of collision indices useless
    #        as they point to locations within this active collider list
    #        breaking here to avoid the issue
    #        but this means only one collision that results in eating can be detected per frame
    #        im sure there is a more elegant solution
    #        """
    #        return (agars, colliders)
    return (agars, colliders)

# get the colliders from a list of agars
def get_colliders(agars):
    colliders = []
    for agar in agars:
        if (agar.rect != None):
            colliders.append(agar.rect)
    return colliders

@jit
def get_postions_and_sizes(agars):
    agar_positions = numpy.zeros(shape = [TEST_COUNT, 2])
    agar_sizes = numpy.zeros(shape = TEST_COUNT)
    for i in range(TEST_COUNT):
        # agar = Agar(None, int_id = i) 
        agar_positions[i] = numpy.array([agars[i].position.x, agars[i].position.y])
        agar_sizes[i] = agars[i].size
    return agar_positions, agar_sizes

@jit
def check_collisions_opt(agar_positions, agar_sizes):
    agar_collisions = numpy.zeros(shape = [TEST_COUNT, 2], dtype = 'i4')
    collision_counter = 0
    for i, position_i in enumerate(agar_positions):
        for j, position_j in enumerate(agar_positions):
            if (i != j):
                distance = numpy.linalg.norm(agar_positions[i] - agar_positions[j])
                if (distance < agar_sizes[i]):
                    # agar i is encompassing agar j
                    agar_collisions[collision_counter] = numpy.array([i, j])
                    collision_counter += 1
    return agar_collisions

def do_collisions(agar, agar_collisions):
    for collision in agar_collisions:
        i, j = (collision[0], collision[1])
        agars[i].on_collision(agars[j])
        if (agars[j].is_eaten):
            # help
            pass

#def on_collision(self, agar) -> None:
#    # cannot collide with self
#    if (self.can_eat == False or self == agar): 
#        return

#    # can always eat blobs
#    if (type(agar) == Blob):
#        if (self.encompasses(agar)):
#            self.eat(agar)
#            return
#    # viruses can't do anything beyond this point (only eat blobs)
#    if (type(self) == Virus):
#        return
#    # on the other hand, if we hit a virus
#    elif (type(agar) == Virus):
#        if (self.mass > VIRUS_EAT_THRESHOLD and self.encompasses(agar)):
#            # eat the virus then pop the cell upto 16 pieces
#            self.eat_virus(agar)
#        else:
#            # hide the cell
#            pass
#    # for collisions between the same agar we merge
#    elif (self.id == agar.id):
#        if (self.parent == None and self.can_merge == True and agar.can_merge == True):
#            self.merge(agar)
#        elif (self.mass >= agar.mass):
#            self.boundary(agar)
#        # else:
#        #   agar.boundary(self)
#    # for collisions between different agars attempt to eat
#    elif (self.mass >= EAT_SIZE_THRESHOLD * agar.mass):
#        if (self.encompasses(agar)):
#            self.eat(agar)
#    # so that boundary is not affected when they try to eat you
#    elif (agar.mass < EAT_SIZE_THRESHOLD * self.mass):
#        self.boundary(agar)
#    return




if __name__ == "__main__":
    agars = setup()
    print("Testing on {0} agars".format(TEST_COUNT))

    start_time = time.time()

    check_collisions(agars)

    run_time = time.time()

    print("Original function time {0:.2f} ms".format( 1000 * (run_time - start_time) ))

    start_time = time.time()

    agar_positions, agar_sizes = get_postions_and_sizes(agars)
    agar_collisions = check_collisions_opt(agar_positions, agar_sizes)
    do_collisions(agars, agar_collisions)

    run_time = time.time()
   
    print("Optimised function time (with compilation)  {0:.2f} ms".format(1000 * (run_time - start_time)))

    start_time = time.time()

    agar_positions, agar_sizes = get_postions_and_sizes(agars)
    agar_collisions = check_collisions_opt(agar_positions, agar_sizes)
    do_collisions(agars, agar_collisions)

    run_time = time.time()
   
    print("Optimised function time (post compilation)  {0:.2f} ms".format(1000 * (run_time - start_time)))