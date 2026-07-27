import sys

# Color Constants
RED = "\033[31m"
LIGHT_BLUE = "\033[96m"
YELLOW = "\033[33m"
RESET = "\033[0m"

def log_error(message: str):
    """Prints a red error message to stderr."""
    print(f"{RED}[ERROR] {message}{RESET}", file=sys.stderr)

def log_info(message: str):
    """Prints a light blue informational message to stderr."""
    print(f"{LIGHT_BLUE}[INFO] {message}{RESET}", file=sys.stderr)

def log_warning(message: str):
    """Prints a red error message to stderr."""
    print(f"{YELLOW}[WARNING] {message}{RESET}", file=sys.stderr)
