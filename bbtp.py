DELIM_INLINE = "|"
DELIM_ENDLINE = "\r\n"

STATUS_BAD_REQUEST = "Bad Request"
STATUS_INCORRECT = "Incorrect"
STATUS_NOT_FOUND = "Not Found"
STATUS_OK = "OK"
STATUS_OUT_OF_ORDER = "Out of Order"
STATUS_UNAUTHENTICATED = "Unauthenticated"
STATUS_UNRECOGNIZED_METHOD = "Unrecognized Method"
STATUS_VERSION_NOT_SUPPORTED = "Version Not Supported"
STATUS_WRONG_NUM_OF_PARAMS = "Wrong Number of Parameters"

def format_header(sender, version):
    return sender + DELIM_INLINE + version

def format_command(method, *args):
    return method if args == None or len(args) == 0 else \
        method + DELIM_INLINE + DELIM_INLINE.join([x.replace(DELIM_ENDLINE, "\n") for x in args])

def format_request(sender, version, method, *args):
    return format_header(sender, version) + DELIM_ENDLINE \
        + format_command(method, *args) + DELIM_ENDLINE

def format_response(status_code, msg=""):
    return status_code + DELIM_ENDLINE \
        + ("" if msg == "" else msg.replace(DELIM_ENDLINE, "\n") + DELIM_ENDLINE)

def parse_header(line):
    tokens = line.split(DELIM_INLINE)
    
    return (tokens[0], tokens[1]) if len(tokens) == 2 else ("", "")

def parse_command(line):
    tokens = line.split(DELIM_INLINE)
    
    return (tokens[0], tokens[1:])

def parse_request(msg):
    lines = msg.split(DELIM_ENDLINE)
    
    sender, version = parse_header(lines[0])
    method, args = parse_command(lines[1] if len(lines) > 0 else "")
    body = lines[2] if len(lines) > 1 else ""
    
    return (sender, version, method, args, body)

def parse_response(msg):
    lines = msg.split(DELIM_ENDLINE)
    
    return (lines[0], lines[1] if len(lines) > 1 else "")

def is_valid_method(s):
    methods = {"FIND", "HINT", "SOLVE", "STATS", "LEADERBOARD"}
    
    return s in methods

def receive_msg(socket):
    return socket.recv(2048).decode()
    
def send_msg(socket, msg):
    socket.send(msg.encode())