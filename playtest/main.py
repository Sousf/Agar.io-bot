### LIBRARIES ###
import tkinter as gui

### LOCAL MODULES ###
from simulation import DumbSimulation
from simulation import PlayerSimulation
from simulation import PlayerAndBotSimulation

class Menu():
    def __init__(self):
        self.menu_screen = self.create_menu()
        self.menu_screen.mainloop()
        return

    # constructs the window
    def create_menu(self) -> gui.Tk:
        # initialize the window
        menu = gui.Tk()

        # constructs the buttons
        self.dumb_bot_button = gui.Button(menu, text ="Dumb Bots", command = self.dumb_bots)
        self.player_bot_button = gui.Button(menu, text ="Player", command = self.player)
        self.player_versus_bots_button = gui.Button(menu, text ="Player and Bots", command = self.player_with_bots)

        # organizes the buttons
        self.dumb_bot_button.pack(side = gui.LEFT)
        self.player_bot_button.pack(side = gui.LEFT)
        self.player_versus_bots_button.pack(side = gui.LEFT)

        return menu

    # runs a simulation with ~20 'dumb' agar bots
    def dumb_bots(self) -> None:
        self.sim = DumbSimulation()
        return None

    # runs a player controlled agar simulation
    def player(self) -> None:
        self.sim = PlayerSimulation()
        return None 

    # runs a player controlled agar simulation with a few 'dumb' bots
    def player_with_bots(self) -> None:
        self.sim = PlayerAndBotSimulation()
        return None 

def __main__():
    # launches a menu
    menu = Menu()    
    return

if __name__ == "__main__":
    __main__()