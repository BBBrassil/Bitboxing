delim = '|'

def find_request(item_code):
    return "FIND" + delim + item_code

def hint_request(item_code):
    return "HINT" + delim + item_code

def solve_request(item_code, solution_code):
    return "SOLVE" + delim + item_code + delim + solution_code

def leaderboard_request(item_code = ""):
    return "LEADERBOARD + ("" if item_code == "" else delim + item_code)

def stats_request(username):
    return "STATS" + delim + username

def send_msg(socket, msg):
    socket.send(msg.encode())

def receive_msg(socket):
    return socket.recv(2048).decode())