import bbtp
from bitboxing_sender import BitboxingSender
from bbdb import PlayerFindStats, PlayerScore
import socket
import json

ip = "127.0.0.1"
port = 9999

qr_codes = [
    "TDQXO",
    "MVMKB",
    "JLPOY",
    "XRUZD",
    "IBQVH"
]

def make_request(msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    
    bbtp.send_msg(s, msg)
    msg = bbtp.receive_msg(s)
    
    s.close()

    return bbtp.parse_response(msg)

def print_main_options():
    print("p\tEnter a puzzle code")
    print("s\tSee your score")
    print("t\tSee the top-scoring players")
    print("q\tQuit")

def print_puzzle_options():
    print("h\tRequest a hint")
    print("s\tTry to solve the puzzle")
    print("t\tSee the top-scoring players for this puzzle")
    print("x\tReturn to main menu")

def print_error(msg):
    print("An error occurred.")
    print(msg)

def print_unknown_error():
    print("Sorry, an unknown error occurred.")

def print_invalid_command():
    print("Invalid command. Try again.")

def print_invalid_code(code):
    print("Sorry, '" + code + "' is not a valid code.")

def print_not_found_yet(code):
    print("You have not found '" + code + "' yet!")

def print_score(msg):
    score = PlayerScore.from_dict(json.loads(msg))

    print(f"Finds:  {score.finds()}")
    print(f"solves: {score.solves()}")

def print_leaderboard(msg):
    scores = [PlayerScore.from_dict(x) for x in json.loads(msg)]

    for i in range(len(scores)):
        print(f"{i}\t{scores[i].player()}")

def print_cache_leaderboard(msg):
    stats = [PlayerFindStats.from_dict(x) for x in json.loads(msg)]

    for i in range(len(stats)):
        print(f"{i + 1}\t{stats[i].player()}")

def login():
    print("Welcome to Bitboxing!")

    name = input("Please enter your name: ")
    while name == "":
        name = input("Try again: ")
    
    print("Hello, " + name + "!")

    return name

def get_command():
    return input("Enter command: ").casefold()

def get_code():
    return input("Enter the code for the puzzle you've found: ")

def get_y_or_n():
    c = input().lower()

    while not (c == "y" or c == "n"):
        c = input("Enter Y or N only. Try again: ").lower()

    return c

def handle_hint(sender, code):
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
    guess = input("What is your guess? ")
    response = make_request(sender.handle_solve(code, guess))

    while response[0] == bbtp.STATUS_INCORRECT:
        print("Sorry, that is not the correct answer.")
        print("Would you like to try again? (Y/N) ")
        ans = get_y_or_n()
        if ans == "y":
            guess = input()
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
    response = make_request(sender.handle_stats(sender.id()))

    if response[0] == bbtp.STATUS_OK:
        print_score(response[1])
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
        print_unknown_error()

def handle_leaderboard(sender):
    response = make_request(sender.handle_leaderboard())

    if response[0] == bbtp.STATUS_OK:
        print_leaderboard(response[1])
    elif response[0] == bbtp.STATUS_EXCEPTION:
        print_error(response[1])
    else:
        print_unknown_error()
        
def handle_cache_leaderboard(sender, code):
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
    print_main_options()

    command = get_command()
    while command != "q":
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

def puzzle_menu(sender):
    code = input("Enter the puzzle code: ")
    response = make_request(sender.handle_find(code))

    if response[0] == bbtp.STATUS_OK or response[0] == bbtp.STATUS_WITHOUT_CHANGE:
        print(response[1])
        print_puzzle_options()

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

def run():
    sender_id = login()
    version = "0.1"
    sender = BitboxingSender(sender_id, version)

    main_menu(sender)

if __name__ == "__main__":
    run()