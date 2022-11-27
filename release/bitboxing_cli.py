import bbtp
from bitboxing_sender import BitboxingSender
from bitboxing_data import FindStatus, PlayerScore
import socket
import json

IP = "127.0.0.1"
PORT = 9999
VERSION = "0.1"
MENU_WIDTH = 80

def make_request(msg):
    """
    Sends a request to the server and fetches a response.

    @param {str} msg BBTP request
    @return {str}    BBTP response
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))
    
    bbtp.send_msg(s, msg)
    msg = bbtp.receive_msg(s)
    
    s.close()

    return bbtp.parse_response(msg)

def print_main_options():
    """
    Prints main menu options.
    """
        
    print("*" * MENU_WIDTH)
    print("Main Menu")
    print("*" * MENU_WIDTH)
    print("P\tEnter a puzzle code")
    print("S\tSee your score")
    print("T\tSee the top-scoring players")
    print("L\tLog out")
    print("Q\tQuit")

def print_puzzle_options(code, question):
    """
    Prints puzzle menu options.

    @param {str} code     Puzzle ID
    @param {str} question Puzzle question
    """

    print("*" * MENU_WIDTH)
    print("Puzzle " + code)
    print("*" * MENU_WIDTH)
    print(question)
    print("H\tRequest a hint")
    print("S\tTry to solve the puzzle")
    print("T\tSee the top-scoring players for this puzzle")
    print("X\tReturn to main menu")

def print_error(msg):
    """"
    Prints an error message for an error.
    
    @param {str} msg Error message
    """

    print("An error occurred.")
    print(msg)

def print_unknown_error():
    """
    Prints an error message for an unknown error.
    """
    
    print("Sorry, an unknown error occurred.")

def print_invalid_command():
    """
    Prints an error message for an invalid console command.
    """
    
    print("Invalid command. Try again.")

def print_invalid_code(code):
    """
    Prints an error message for an invalid puzzle code.

    @param {str} code Puzzle ID
    """
    
    print("Sorry, '" + code + "' is not a valid code.")

def print_not_found_yet(code):
    """
    Prints an error message for a puzzle that the user hasn't found yet.

    @param {str} code Puzzle ID
    """

    print("You have not found '" + code + "' yet!")

def print_score(msg):
    """
    Prints a BBTP SCORE response payload.
    
    @param {str} msg JSON object containing score data
    """
    
    score = PlayerScore.from_dict(json.loads(msg))

    print(f"Finds:  {score.finds()}")
    print(f"solves: {score.solves()}")

def print_leaderboard(msg):
    """
    Prints a BBTP LEADERBOARD response payload.
    
    @param {str} msg List of PlayerScore objects as JSON-formatted string
    """

    leaderboard = [PlayerScore.from_dict(x) for x in json.loads(msg)]

    print("".ljust(4) + "  " + "Player".ljust(40) + "  " + "Finds".ljust(6) + "  " + "Solves".ljust(6))
    for i in range(len(leaderboard)):
        x = leaderboard[i]
        print(str(i + 1).ljust(4) + "  " + x.player().ljust(40) + "  " + str(x.finds()).ljust(6) + "  " + str(x.solves()).ljust(6))

def print_cache_leaderboard(msg):
    """
    Prints a BBTP CACHE_LEADERBOARD response payload.
    
    @param {str} msg List of player names as JSON-formatted string
    """
    
    leaderboard = json.loads(msg)

    for i in range(len(leaderboard)):
        print(f"{i + 1}\t{leaderboard[i]}")

def login():
    """"
    Validates a
    @return {BitboxingSender} Authenticated BBTP sender, None if login failed
    """
    
    username = input("Username: ")
    if username == "":
        return None
    
    password = input("Password: ")
    
    sender = BitboxingSender(username, VERSION)

    response = make_request(sender.handle_login(password))
    
    if response[0] == bbtp.STATUS_UNAUTHENTICATED:
        response = make_request(sender.handle_register(password))

        if response[0] == bbtp.STATUS_OK:
            response = make_request(sender.handle_login(password))
    
    if response[0] == bbtp.STATUS_OK:
        return sender
    elif response[0] == bbtp.STATUS_INCORRECT:
        print("Incorrect password!")
        return None
    else:
        print_unknown_error()
        return None

def get_command():
    """
    Gets a console command from the user.

    @return {str} Lowercase
    """

    return input("Enter command: ").lower()

def get_code():
    """
    Gets a puzzle code from the user.

    @return {str} Lowercase
    """
    
    return input("Enter the code for the puzzle you've found: ")

def get_y_or_n():
    """
    Gets the letter y or n from the user for a yes or no response.

    @return {str} Lowercase y or n
    """
    
    c = input().lower()

    while not (c == "y" or c == "n"):
        c = input("Enter Y or N only. Try again: ").lower()

    return c

def handle_hint(sender, code):
    """
    Fetches a hint for a puzzle.

    @param {BitboxingSender} sender Authenticated BBTP sender
    @param {str}             code   Puzzle ID
    """

    response = make_request(sender.handle_hint(code))
    if response[0] == bbtp.STATUS_OK:
        print(response[1])
    elif response[0] == bbtp.STATUS_OUT_OF_ORDER:
        print_not_found_yet(code)
    elif response[0] == bbtp.STATUS_NOT_FOUND:
        print_invalid_code(code)
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
        print_unknown_error()

def handle_solve(sender, code):
    """
    Allows a player to try to solve a puzzle.

    @param {BitboxingSender} sender Authenticated BBTP sender
    @param {str}             code   Puzzle ID
    """

    guess = input("What is your guess? ")
    response = make_request(sender.handle_solve(code, guess))

    while response[0] == bbtp.STATUS_INCORRECT:
        print("Sorry, that is not the correct answer.")
        print("Would you like to try again? (Y/N) ")
        ans = get_y_or_n()
        if ans == "y":
            guess = input("What is your guess? ")
            response = make_request(sender.handle_solve(code, guess))
        else:
            return

    if response[0] == bbtp.STATUS_OK:
        print("Correct!")
    elif response[0] == bbtp.STATUS_OUT_OF_ORDER:
        print("You have already solved this!")
    elif response[0] == bbtp.STATUS_NOT_FOUND:
        print_invalid_code(code)
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
       print_unknown_error()

def handle_score(sender):
    """
    Fetches a player score.

    @param {BitboxingSender} sender Authenticated BBTP sender
    """

    response = make_request(sender.handle_score(sender.id()))

    if response[0] == bbtp.STATUS_OK:
        print_score(response[1])
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
        print_unknown_error()

def handle_leaderboard(sender):
    """
    Fetches the game leaderboard.

    @param {BitboxingSender} sender Authenticated BBTP sender
    """
    
    response = make_request(sender.handle_leaderboard())

    if response[0] == bbtp.STATUS_OK:
        print_leaderboard(response[1])
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
        print_unknown_error()
        
def handle_cache_leaderboard(sender, code):
    """
    Fetches a cache leaderboard.

    @param {BitboxingSender} sender Authenticated BBTP sender
    @param {str}             code   Puzzle ID
    """

    response = make_request(sender.handle_cache_leaderboard(code))

    if response[0] == bbtp.STATUS_OK:
        print_cache_leaderboard(response[1])
    elif response[0] == bbtp.STATUS_NOT_FOUND:
        print_invalid_code(code)
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
        print_unknown_error()

def main_menu(sender):
    """
    Launches the main menu menu with the following options:
    - Enter a puzzle code
    - Display player score
    - Display top scorers
    - Log out
    - Quit

    @param {BitboxingSender} Authenticated BBTP sender
    """

    print_main_options()

    command = get_command()
    while command != "q" and command != "l":
        if command == "p":
            puzzle_menu(sender)
            print_main_options()
        elif command == "s":
            handle_score(sender)
        elif command == "t":
            handle_leaderboard(sender)
        else:
            print_invalid_command()
        command = get_command()
    
    return command == "q"

def puzzle_menu(sender):
    """
    Launches the puzzle menu. Asks the user to enter a puzzle code, then accepts the following options:
    - Request a hint
    - Try to solve the puzzle
    - See top scorers for this puzzle
    - Return to main menu

    @param {BitboxingSender} Authenticated BBTP sender
    """

    code = input("Enter the puzzle code: ")
    response = make_request(sender.handle_find(code))

    if response[0] == bbtp.STATUS_OK or response[0] == bbtp.STATUS_WITHOUT_CHANGE:
        print_puzzle_options(code, response[1])

        command = get_command()
        while command != "x":
            if command == "h":
                handle_hint(sender, code)
            elif command == "s":
                handle_solve(sender, code)
            elif command == "t":
                handle_cache_leaderboard(sender, code)
            else:
                print_invalid_command()
            command = get_command()
    elif response[0] == bbtp.STATUS_NOT_FOUND:
        print_invalid_code(code)
    else:
        print_unknown_error()

if __name__ == "__main__":
    done = False
    
    while not done:
        print("*" * MENU_WIDTH)
        print("Welcome to Bitboxing!")
        print("*" * MENU_WIDTH)

        sender = login()
        
        while not sender:
            command = input("Try again? (Y/N) ").casefold()
            if command == "y":
                sender = login()
            else:
                break
        
        if sender:
            done = main_menu(sender)