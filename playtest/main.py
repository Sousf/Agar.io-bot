### LIBRARIES ###
import tkinter as gui;

### LOCAL MODULES ###
from simulation import DumbSimulation;
from simulation import PlayerSimulation;
from simulation import PlayerAndBotSimulation;


# runs a simulation with ~20 'dumb' agar bots
def dumbBots() -> None:
    sim = DumbSimulation();
    return None;

# runs a player controlled agar simulation
def player() -> None:
    sim = PlayerSimulation();
    return None; 

# runs a player controlled agar simulation with a few 'dumb' bots
def playerWithBots() -> None:
    sim = PlayerAndBotSimulation();
    return None; 

# constructs the window
def createMenu() -> gui.Tk:
    # initialize the window
    menu = gui.Tk();

    # constructs the buttons
    dumbBotButton = gui.Button(menu, text ="Dumb Bots", command = dumbBots);
    playerBotButton = gui.Button(menu, text ="Player", command = player);
    playerVersusBotButton = gui.Button(menu, text ="Player and Bots", command = playerWithBots);

    # organizes the buttons
    dumbBotButton.pack(side = gui.LEFT);
    playerBotButton.pack(side = gui.LEFT);
    playerVersusBotButton.pack(side = gui.LEFT);

    return menu;

def __main__():
    menu = createMenu();
    menu.mainloop();
    return;

if __name__ == "__main__":
    __main__();