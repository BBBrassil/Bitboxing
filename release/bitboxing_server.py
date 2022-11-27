from bitboxing_receiver import BitboxingReceiver
import bbtp
import socket

PORT = 9999

def handle_request(msg, receiver):
    """
    Responds to client requests.

    @param {str}               msg      BBTP request
    @param {BitboxingReceiver} receiver Database
    @return {str}                       BBTP response
    """
    sender, version, method, args, body = bbtp.parse_request(msg)

    print(f"Server received request from '{sender}':")
    print(f"{method} {args}")

    try:
        if sender == "" or version == "" or method == "":
            return receiver.handle_error(sender, bbtp.STATUS_BAD_REQUEST)
        elif not receiver.supports(version):
            return receiver.handle_error(sender, bbtp.STATUS_VERSION_NOT_SUPPORTED)
        elif method != "REGISTER" and not receiver.is_authenticated(sender):
            return receiver.handle_error(sender, bbtp.STATUS_UNAUTHENTICATED)
        elif not bbtp.is_valid_method(method):
            return receiver.handle_error(sender, bbtp.STATUS_UNRECOGNIZED_METHOD)
        elif method == "REGISTER" and len(args) == 1:
            return receiver.handle_register(sender, args[0])
        elif method == "LOGIN" and len(args) == 1:
            return receiver.handle_login(sender, args[0])
        elif method == "FIND" and len(args) == 1:
            return receiver.handle_find(sender, args[0])
        elif method == "HINT" and len(args) == 1:
            return receiver.handle_hint(sender, args[0])
        elif method == "SOLVE" and len(args) == 2:
            return receiver.handle_solve(sender, args[0], args[1])
        elif method == "SCORE" and len(args) == 1:
            return receiver.handle_score(sender, args[0])
        elif method == "LEADERBOARD" and len(args) == 0:
            return receiver.handle_leaderboard(sender)
        elif method == "LEADERBOARD" and len(args) == 1:
            return receiver.handle_leaderboard(sender, args[0])
        elif method == "CACHE_LEADERBOARD" and len(args) == 1:
            return receiver.handle_cache_leaderboard(sender, args[0])
        elif method == "CACHE_LEADERBOARD" and len(args) == 2:
            return receiver.handle_cache_leaderboard(sender, args[0], args[1])
        else:
            return receiver.handle_error(sender, bbtp.STATUS_WRONG_NUM_OF_PARAMS)
    except Exception as ex:
            return receiver.handle_error(sender, bbtp.STATUS_EXCEPTION, repr(Exception) + ": " + repr(ex))

def serve(receiver):
    """
    Launches the server.

    @param {BitboxingReceiver} receiver
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.bind(("", PORT))
    s.listen(100)
    
    print(f"Server is listening to port {PORT}...")
    
    try:
        while True:
            cs, address = s.accept()
            
            request = bbtp.receive_msg(cs)
            response = handle_request(request, receiver)
            
            bbtp.send_msg(cs, response)
    except Exception as ex:
        print(f"Error: '{repr(ex)}'!")
        print("Server going offline...")

if __name__ == "__main__":
    version = "0.1"
    path = "bitboxing.db"
    receiver = BitboxingReceiver(version, path)
    
    serve(receiver)