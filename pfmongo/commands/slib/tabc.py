import readline
from typing import Optional
from pfmongo.commands import smash
from argparse import Namespace
import pudb

testfiles: list[str] = [
    "lld.json",
    "aphid",
    "berry",
    "balloon",
    "banana",
    "ball",
    "cherry",
    "cherub",
    "duck",
]

choices: list[str] = []
fscmd: str = ""


def completer(text: str, state: int) -> Optional[str]:
    global choices, fscmd
    hits: list[str] = [choice for choice in choices if choice.startswith(text)]
    if state < len(hits):
        for index, item in enumerate(hits):
            if item in text:
                choices = testfiles
                state = index
                if not fscmd:
                    fscmd = text
                break  # Exit the loop after finding the first match
        return hits[state]
    else:
        return None


readline.set_completer(completer)
readline.parse_and_bind("tab: complete")


def choice_get(options: Namespace) -> str:
    global choices, fscmd
    choices = smash.fscommand
    fscmd = ""
    while True:
        user_input: str = input(smash.prompt_get(options)).strip()
        # pudb.set_trace()
        if choices == testfiles:
            user_input = "".join(user_input.split()[1:])
        if not user_input:  # If no input, show all choices
            print("Possible choices:", ", ".join(choices))
            continue
        matching_choices: list[str] = [
            choice for choice in choices if choice.startswith(user_input)
        ]
        if len(matching_choices) == 1:  # If only one choice left, return it
            return matching_choices[0]
        elif (
            len(matching_choices) > 1
        ):  # If multiple choices, prompt again with completion
            completion: Optional[str] = completer(user_input, 0)
            if completion is not None:
                user_input += completion[
                    len(user_input) :
                ]  # Update user_input with completion
                readline.redisplay()
        elif len([choice for choice in choices if choice in user_input]):
            return user_input
        else:
            print("No matches found. Please try again.")
            continue
