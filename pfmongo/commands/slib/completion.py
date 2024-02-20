import curses
from typing import List

def capture_tab_and_process_input(prompt: str, options: List[str]) -> str:
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.keypad(True)

    user_input = ''
    cursor_position = 0

    while True:
        # stdscr.clear()
        stdscr.addstr(0, 0, prompt + user_input)
        stdscr.move(0, len(prompt) + cursor_position)
        stdscr.refresh()

        event = stdscr.getch()
        if event == ord('\t'):
            # If Tab is pressed without typing anything, show all options
            if not user_input:
                filtered_options = options
            else:
                # Process the input string so far to generate the list of options
                filtered_options = [option for option in options if option.startswith(user_input)]
            if filtered_options:
                selected_option = select_option(filtered_options, stdscr)
                if selected_option is not None:
                    user_input = selected_option
                    cursor_position = len(user_input)
        elif event == ord('\x1b'):  # Escape key
            user_input = ''
            cursor_position = 0
        elif event == curses.KEY_ENTER or event == 10:
            break  # Exit the loop and return user input
        elif event == curses.KEY_BACKSPACE or event == 127:
            if cursor_position > 0:
                user_input = user_input[:cursor_position - 1] + user_input[cursor_position:]
                cursor_position -= 1
        elif event == curses.KEY_LEFT:
            cursor_position = max(0, cursor_position - 1)
        elif event == curses.KEY_RIGHT:
            cursor_position = min(len(user_input), cursor_position + 1)
        elif event >= 32 and event <= 126:  # printable characters
            user_input = user_input[:cursor_position] + chr(event) + user_input[cursor_position:]
            cursor_position += 1

        # Show possible responses only when Tab key is pressed
        if event == ord('\t') and filtered_options:
            stdscr.addstr(1, 0, 'Possible responses: ')
            for i, option in enumerate(filtered_options):
                stdscr.addstr(option + ' ' if i < len(filtered_options) - 1 else option)
            stdscr.refresh()

    curses.endwin()  # Reset the console
    return user_input

def select_option(options: List[str], stdscr) -> str:
    selected_index = 0
    while True:
        stdscr.move(1, 0)
        stdscr.clrtoeol()
        stdscr.addstr('Possible responses: ')
        for i, option in enumerate(options):
            stdscr.addstr(option + ' ', curses.A_REVERSE if i == selected_index else curses.A_NORMAL)
        stdscr.refresh()

        event = stdscr.getch()
        if event == curses.KEY_RIGHT:
            selected_index = (selected_index + 1) % len(options)
        elif event == curses.KEY_LEFT:
            selected_index = (selected_index - 1) % len(options)
        elif event == curses.KEY_ENTER or event == 10:
            return options[selected_index]

# Example usage:
prompt = "Enter your input: "
options = ["apple", "banana", "ball", "cherry", "church", "grape", "lemon", "aphid"]
result = capture_tab_and_process_input(prompt, options)
print("You selected:", result)

