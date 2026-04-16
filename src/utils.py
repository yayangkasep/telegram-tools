import os

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a formatted header and clears the screen."""
    clear_screen()
    print("========================================")
    print(f"        {title.upper()}")
    print("========================================\n")

def get_integer_input(prompt, min_val=None, max_val=None):
    """Helper to safely get an integer input from the user within a range."""
    while True:
        try:
            choice = int(input(prompt))
            if min_val is not None and choice < min_val:
                print(f"Invalid choice. Minimum is {min_val}.")
                continue
            if max_val is not None and choice > max_val:
                print(f"Invalid choice. Maximum is {max_val}.")
                continue
            return choice
        except ValueError:
            print("Please enter a valid number.")
