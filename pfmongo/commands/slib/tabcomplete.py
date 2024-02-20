
from typing import Optional, Union

import readline
import rlcompleter
import  pudb

class SmashCompleter(rlcompleter.Completer):
    def get_completions(self, text: str, state: int) -> Optional[list[str]]:
        """
        Gets completion options based on the current input.

        Args:
            text: The current input text (str).
            state: The completion state (int, 0 for first completion).

        Returns:
            A list of completion options (List[str]) or None if no options available.
        """

        current_word = text.split()[-1]
        if not current_word:
            return []

        pudb.set_trace()
        completions = generate_completions(current_word)
        completions = [c for c in completions if c.startswith(current_word)]

        if state == 0:
            return completions
        else:
            # Return next completion based on state (if applicable)
            return None

def initialize_readline() -> None:
    """
    Initializes the readline module for tab completion.

    Raises:
        RuntimeError: If readline is not available.
    """

    if not hasattr(readline, '__doc__'):
        raise RuntimeError("Readline module not available.")

    # Disable default completion (if present)
    readline.parse_and_bind("tab: ")

    # Initialize custom completer
    completer   = SmashCompleter()
    readline.set_completer(completer.get_completions)
    readline.read_init_file()


# Replace `generate_completions` with your actual function
def generate_completions(current_word: str) -> list[str]:
    """
    Generates completion options based on the current word.

    Args:
        current_word: The current word the user is typing (str).

    Returns:
        A list of possible completions (List[str]).
    """

    # Implement your logic to generate completion options based on current_word
    # (e.g., access a database, search files, or use a dictionary)
    choices:list = ["apple", "aphid", "banana", "ball", "cherry", "duck"]
    return [option for option in choices if option.startswith(current_word)]

def my_repl():
    initialize_readline()
    while True:
        user_input = input("smash>>> ")
        print(user_input)
        # Process user_input here (e.g., call your command handler)

my_repl()
