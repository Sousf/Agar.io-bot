""" LIBRARIES """
import tkinter as gui

""" LOCAL MODULES """
from simulation import Simulation
from debug import Debug

class Menu():
    def __init__(self):

        Debug.menu("Initialized")

        self.menu_screen = self.create_menu()
        self.menu_screen.mainloop()
        return

    # constructs the window
    def create_menu(self) -> gui.Tk:
        # initialize the window
        menu = gui.Tk()

        # constructs the buttons
        self.basic_button = gui.Button(menu, text ="Basic", command = self.basic)

        # organizes the buttons
        self.basic_button.pack(side = gui.LEFT)

        return menu

    # runs a simulation with ~20 'dumb' agar bots
    def basic(self) -> None:
        self.sim = Simulation(caption = "Basic Simulation")
        return None


def __main__():
    # launches a menu
    menu = Menu()    
    return

if __name__ == "__main__":
    __main__()
