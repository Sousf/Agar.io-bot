### LOCAL MODULES ###
from simulation import DumbSimulation;
from simulation import PlayerSimulation;
from simulation import PlayerAndBotSimulation;


# Runs a simulation with ~20 'dumb' agar bots
def dumbBots() -> None:
    sim = DumbSimulation();
    return None;

# Runs a player controlled agar simulation
def player() -> None:
    sim = PlayerSimulation();
    return None; 

# Runs a player controlled agar simulation with a few 'dumb' bots
def playerWithBots() -> None:
    sim = PlayerAndBotSimulation();
    return None; 

def __main__():
    player();
    return;

if __name__ == "__main__":
    __main__();