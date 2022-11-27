DELIM_INLINE = "|"
DELIM_ENDLINE = "\r\n"

STATUS_BAD_REQUEST = "Bad Request"
STATUS_EXCEPTION = "Exception"
STATUS_INCORRECT = "Incorrect"
STATUS_NOT_FOUND = "Not Found"
STATUS_OK = "OK"
STATUS_OUT_OF_ORDER = "Out of Order"
STATUS_UNAUTHENTICATED = "Unauthenticated"
STATUS_UNRECOGNIZED_METHOD = "Unrecognized Method"
STATUS_VERSION_NOT_SUPPORTED = "Version Not Supported"
STATUS_WITHOUT_CHANGE = "Without Change"
STATUS_WRONG_NUM_OF_PARAMS = "Wrong Number of Parameters"

def format_header(sender, version):
    """
    Formats a BBTP header.
    <sender> | version

    @param {str} sender  Username
    @param {str} version BBTP version (e.g. 0.1)
    @return {str}
    """

    return sender + DELIM_INLINE + version

def format_command(method, *args):
    """
    Formats a BBTP command.
    <method> | <arg0> | <arg1> | ...

    @param {str} method  BBTP method (e.g. FIND)
    @param {list} *args  Method arguments
    @return {str}
    """

    return method if args == None or len(args) == 0 else \
        method + DELIM_INLINE + DELIM_INLINE.join([x.replace(DELIM_ENDLINE, "\n") for x in args])

def format_request(sender, version, method, *args):
    """
    Formats a BBTP request.
    
    <sender> | version \r\n
    <method> | <arg0> | <arg1> | ... \r\n
    
    @param {str} sender  Username
    @param {str} version BBTP version (e.g. 0.1)
    @param {str} method  BBTP method (e.g. FIND)
    @param {list} *args  Method arguments
    @return {str}
    """

    return format_header(sender, version) + DELIM_ENDLINE \
        + format_command(method, *args) + DELIM_ENDLINE

def format_response(status_code, msg=""):
    """
    Formats a BBTP response.
    """
    return status_code + DELIM_ENDLINE \
        + ("" if msg == "" else msg.replace(DELIM_ENDLINE, "\n") + DELIM_ENDLINE)

def parse_header(line):
    """
    Parses a BBTP header, splitting into tokens.

    @param {str} line BBTP header
    @return {tuple (str, str)} (sender, version)
    """

    tokens = line.split(DELIM_INLINE)
    
    return (tokens[0], tokens[1]) if len(tokens) == 2 else ("", "")

def parse_command(line):
    """
    Parses a BBTP command, splitting into tokens.

    @param {str} line BBTP command
    @return {tuple (str, list of str)} (method, args)
    """
    
    tokens = line.split(DELIM_INLINE)
    
    return (tokens[0], tokens[1:])

def parse_request(msg):
    """
    Parses a BBTP request, splitting into tokens.

    @param {str} msg BBTP request
    @return {tuple (str, str, str, list of str, str)} (sender, version, method, args, body)
    """

    lines = msg.split(DELIM_ENDLINE)
    
    sender, version = parse_header(lines[0])
    method, args = parse_command(lines[1] if len(lines) > 0 else "")
    body = lines[2] if len(lines) > 1 else ""
    
    return (sender, version, method, args, body)

def parse_response(msg):
    """
    Parses a BBTP response, splitting into tokens.

    @param {str} msg BBTP response
    @return {type (str, str)} (status code, body)
    """

    lines = msg.split(DELIM_ENDLINE)
    
    return (lines[0], lines[1] if len(lines) > 1 else "")

def is_valid_method(s):
    """
    Checks if a method name is valid.

    @param {str} s Method name to check
    @return {bool} True if s is supported.
    """

    methods = {"REGISTER", "LOGIN", "FIND", "HINT", "SOLVE", "SCORE", "LEADERBOARD", "CACHE_LEADERBOARD"}
    
    return s in methods

def receive_msg(socket):
    """
    Receives a message through TCP.

    @param {Socket} socket Open socket
    @return {str}          Message of up to 2048 bytes
    """
    
    return socket.recv(2048).decode()
    
def send_msg(socket, msg):
    """
    Sends a message through TCP.

    @param {Socket} socket Open socket
    @param {str}    msg    Message of up to 2048 bytes
    """

    socket.send(msg.encode())