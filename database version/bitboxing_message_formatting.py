# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 21:13:36 2022

@author: mikkelsonm
"""

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

"""
Methods for formatting and parsing messages:
    Command: Sender|Method|args[1]|args[2]|...|...
    
    Sender: username
    Method: protocol, i.e. FOUND, HINT, LEADERBOARD, etc.
    
"""

'''
formats client request message
parameters:
    sender - username
    method - protocol
    args - arguments for protocol
returns:
    formatted message as a string
'''

def format_request(sender, method, *args):
    if args == None or len(args) == 0:
        return sender + DELIM_INLINE + method
    else:
        return sender + DELIM_INLINE + method + DELIM_INLINE + DELIM_INLINE.join([x for x in args])

'''
formats server response message
parameters:
    status_code - indicator of request success
    msg - string giving more detail to status code or fulfilling request
'''
def format_response(status_code, msg=""):
    return status_code + DELIM_INLINE + msg

'''
server method for parsing client request message
parameters:
    msg - client message as string
returns:
    tuple containing (username, protocol, args)
'''

def parse_request(msg):
    tokens = msg.split(DELIM_INLINE)
    if len(tokens) >= 2:
        sender = tokens[0]
        method = tokens[1]
        if len(tokens) > 2:
            args = tokens[2:]
        else:
            args = ""
    else:
        sender = ""
        method = ""
        args = ""
    
    return (sender, method, args)

'''
client method for parsing server response message
parameters:
    msg - server response message as string
returns:
    tuple containing (status_code, message)
'''
def parse_response(msg):
    tokens = msg.split(DELIM_INLINE)
    
    if len(tokens) == 2:
        return (tokens[0], tokens[1])
    else:
        return ("", "")

'''
verifies that the protocol is valid
'''
def is_valid_method(protocol):
    methods = {"LOGIN", "NEW_USER", "FIND", "HINT", "SOLVE", "STATS", "LEADERBOARD", "CACHE_LEADERBOARD"}
    
    return protocol in methods

def receive_msg(socket):
    return socket.recv(2048).decode()
    
def send_msg(socket, msg):
    socket.send(msg.encode())


def main():
    '''
    #test format_request
    print(format_request("A", "FIND", "3"))
    print(format_request("B", "HINT", "1"))
    print(format_request("C", "STATS"))
    
    #test parse_request
    print(parse_request(format_request("A", "FIND", "3")))
    print(parse_request(format_request("B", "HINT", "1")))
    print(parse_request(format_request("C", "STATS")))
    
    #test format_response
    print(format_response("1", STATUS_BAD_REQUEST))
    print(format_response("1", STATUS_NOT_FOUND))
    print(format_response("1", STATUS_BAD_REQUEST + "\n" + STATUS_NOT_FOUND))
    
    #test parse_response
    print(parse_response(format_response("1", STATUS_BAD_REQUEST)))
    print(parse_response(format_response("1", STATUS_NOT_FOUND)))
    print(parse_response(format_response("1", STATUS_BAD_REQUEST + "\n" + STATUS_NOT_FOUND)))
    '''
    print(is_valid_method("hello"))
    print(is_valid_method("FIND"))

if __name__ == '__main__':
    main()



