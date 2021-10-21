import sys
sys.path.append("..")
from agar import *

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

if __name__ == "__main__":
    print("Successfully ran Player")
