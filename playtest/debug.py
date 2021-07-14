from dataclasses import dataclass
from colorama import Fore, Back, Style
from colorama import init
init(autoreset=True)

LOG_TAG : str = "[Log]: "; DEBUG_LOG : bool = False
WARNING_TAG : str = "[Warning]: "; DEBUG_WARNING : bool = True
MENU_TAG : str = "[Menu]: "; DEBUG_MENU : bool = True
SIMULATION_TAG : str = "[Simulation]: "; DEBUG_SIMULATION : bool = False
AGAR_TAG : str = "[Agar]: "; DEBUG_AGAR : bool = True

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

    def agar(message : str, fore = Fore.BLUE, back = Back.BLACK) -> None:
        if (DEBUG_AGAR == False): return None
        print(fore + back + AGAR_TAG + message);
        return


if __name__ == "__main__":
    Debug.warning("hello");