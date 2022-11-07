import bbtp
from bitboxing_sender import BitboxingSender
import socket
import test

ip = "127.0.0.1"
port = 9999

sender_id = "A"
version = "0.1"
sender = BitboxingSender(sender_id, version)

for x in "12345":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    
    request = sender.handle_hint(x)
    bbtp.send_msg(s, request)
    test.print_request(request)
    response = bbtp.receive_msg(s)
    test.print_response(response)
    
    s.close()