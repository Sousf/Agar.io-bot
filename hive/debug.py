from dataclasses import dataclass
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

LOG_TAG : str = "[Log]: "; DEBUG_LOG : bool = False
WARNING_TAG : str = "[Warning]: "; DEBUG_WARNING : bool = True
MENU_TAG : str = "[Menu]: "; DEBUG_MENU : bool = True
SIMULATION_TAG : str = "[Simulation]: "; DEBUG_SIMULATION : bool = True; DEBUG_SIMULATION_UPDATE = True;
PLAYER_TAG : str = "[Player]: "; DEBUG_PLAYER : bool = True; DEBUG_PLAYER_HAND : bool = True
HIVE_TAG : str = "[Hive]: "; DEBUG_HIVE : bool = True

@dataclass
class Debug():

    def log(message : str, fore = Fore.WHITE, back = Back.BLACK) -> None:
        if (LOG_TAG == False): return None
        print(fore + back + LOG_TAG + message);
        return
    
    def warning(message : str, fore = Fore.RED, back = Back.BLACK) -> None:
        if (DEBUG_WARNING == False): return None
        print(fore + back + WARNING_TAG + message);
        return

    def menu(message : str, fore = Fore.GREEN, back = Back.BLACK) -> None:
        if (DEBUG_MENU == False): return None
        print(fore + back + MENU_TAG + message);
        return

    def simulation(message : str, fore = Fore.YELLOW, back = Back.BLACK) -> None:
        if (DEBUG_SIMULATION == False): return None
        print(fore + back + SIMULATION_TAG + message);
        return

    def simulation_update(message : str, fore = Fore.YELLOW, back = Back.BLACK) -> None:
        if (DEBUG_SIMULATION_UPDATE == False): return None
        print(fore + back + SIMULATION_TAG + message);
        return

    def player(message : str, fore = Fore.BLUE, back = Back.BLACK) -> None:
        if (DEBUG_PLAYER == False): return None
        print(fore + back + PLAYER_TAG + message);
        return

    def player_hand(hand : list, fore = Fore.BLUE, back = Back.BLACK) -> None:
        if (DEBUG_PLAYER_HAND == False): return None
        message = ""
        for piece in hand:
            message += piece.short_id + ", "
        print(fore + back + PLAYER_TAG + message);
        return

    def hive(message : str, fore = Fore.CYAN, back = Back.BLACK) -> None:
        if (DEBUG_HIVE == False): return None
        print(fore + back + HIVE_TAG + message);
        return

if __name__ == "__main__":
    Debug.warning("hello");