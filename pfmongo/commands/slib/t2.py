import readline
from typing import Optional
import pudb

fruits: list[str] = ["apple", "aphid", "berry", "balloon", "banana", "ball", "cherry", "cherub", "duck"]
colors: list[str] = ["red", "darkred", "green", "darkgreen"]

current_choices: list[str] = colors
first_word:str      = ""

def completer(text: str, state: int) -> Optional[str]:
    global current_choices, first_word
#    pudb.set_trace()
    options: list[str] = [choice for choice in current_choices if choice.startswith(text)]
    if state < len(options):
        for index, item in enumerate(options):
            if text == item:
                current_choices     = fruits
                state = index
                if not first_word:
                    first_word = text
                break  # Exit the loop after finding the first match

        return options[state]
    else:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def get_choice(prompt: str) -> str:
    global current_choices, first_word
    current_choices = colors
    first_word      = ""
    while True:
        user_input: str = input(prompt).strip()
        if current_choices == fruits:
            user_input = user_input.split()[1]
        if not user_input:  # If no input, show all choices
            print("Possible choices:", ", ".join(current_choices))
            continue
        matching_choices: list[str] = [choice for choice in current_choices if choice.startswith(user_input)]
        if len(matching_choices) == 1:  # If only one choice left, return it
            return matching_choices[0]
        elif len(matching_choices) > 1:  # If multiple choices, prompt again with completion
            completion: Optional[str] = completer(user_input, 0)
            if completion is not None:
                user_input += completion[len(user_input):]  # Update user_input with completion
                readline.redisplay()
        else:
            print("No matches found. Please try again.")
            continue

# Example REPL usage:
while True:
    prompt: str = "Enter your choice: "
    choice: str = get_choice(prompt)
    print("You selected:", first_word + ' ' + choice)


