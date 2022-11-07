import bbtp
from bitboxing_sender import BitboxingSender
import socket
import test

ip = "127.0.0.1"
port = 9999

sender_id = "A"
version = "0.1"
sender = BitboxingSender(sender_id, version)

def make_request(ip, port, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    
    bbtp.send_msg(s, msg)
    test.print_request(msg)
    msg = bbtp.receive_msg(s)
    test.print_response(msg)
    
    s.close()
    
for x in "12345":
    make_request(ip, port, sender.handle_find(x))
    make_request(ip, port, sender.handle_hint(x))