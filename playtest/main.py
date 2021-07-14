### LIBRARIES ###
import tkinter as gui;

### LOCAL MODULES ###
from simulation import DumbSimulation;
from simulation import PlayerSimulation;
from simulation import PlayerAndBotSimulation;

class Menu():
    def __init__(self):
        self.menuScreen = self.createMenu();
        self.menuScreen.mainloop();
        return;

    # constructs the window
    def createMenu(self) -> gui.Tk:
        # initialize the window
        menu = gui.Tk();

        # constructs the buttons
        self.dumbBotButton = gui.Button(menu, text ="Dumb Bots", command = self.dumbBots);
        self.playerBotButton = gui.Button(menu, text ="Player", command = self.player);
        self.playerVersusBotButton = gui.Button(menu, text ="Player and Bots", command = self.playerWithBots);

        # organizes the buttons
        self.dumbBotButton.pack(side = gui.LEFT);
        self.playerBotButton.pack(side = gui.LEFT);
        self.playerVersusBotButton.pack(side = gui.LEFT);

        return menu;

    # runs a simulation with ~20 'dumb' agar bots
    def dumbBots(self) -> None:
        self.sim = DumbSimulation();
        return None;

    # runs a player controlled agar simulation
    def player(self) -> None:
        self.sim = PlayerSimulation();
        return None; 

    # runs a player controlled agar simulation with a few 'dumb' bots
    def playerWithBots(self) -> None:
        self.sim = PlayerAndBotSimulation();
        return None; 

def __main__():
    # launches a menu
    menu = Menu();    
    return;

if __name__ == "__main__":
    __main__();