import logging
from colorama import Fore, Style, init

init(autoreset=True)

class ColorFormatter(logging.Formatter):
    COLOR_MAP = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.WHITE,
        "WARNING": Fore.YELLOW + Style.BRIGHT,
        "ERROR": Fore.RED + Style.BRIGHT,
        "CRITICAL": Fore.WHITE + Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        msg = super().format(record)
        color = self.COLOR_MAP.get(record.levelname, "")
        return f"{color}{msg}{Style.RESET_ALL}"
