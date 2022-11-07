import bbtp
from bitboxing_sender import BitboxingSender
import socket
import test

import time


ip = "127.0.0.1"
port = 9999

sender_id = "A"
version = "0.1"
sender = BitboxingSender(sender_id, version)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))

request = sender.handle_cache_leaderboard("3")
bbtp.send_msg(s, request)
test.print_request(request)
response = bbtp.receive_msg(s)
test.print_response(response)

s.close()