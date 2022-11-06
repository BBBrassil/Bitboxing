from bitboxing_receiver import BitboxingReceiver
from bitboxing_sender import BitboxingSender
from bitboxing_server import handle_request
import bbtp

WIDTH = 80

def print_request(msg):
    sender, version, method, args, body = bbtp.parse_request(msg)
    
    print()
    print("*" * WIDTH)
    print("Request")
    print("-" * WIDTH)
    print(f"Sender          {sender}")
    print(f"Version         {version}")
    print(f"Method          {method}")
    print(f"Args            ({len(args)})")
    for i in range(len(args)):
        print(" " * 16 + f"{i}: {args[i]}")
    print(f"Body Length     {len(body)}")
    print("-" * WIDTH)
    print(body)
    print("*" * WIDTH)
    print()
    
def print_response(msg):
    status_code, body = bbtp.parse_response(msg)
    
    print()
    print("*" * WIDTH)
    print("Response")
    print("-" * WIDTH)
    print(f"Status Code     {status_code}")
    print(f"Body            ({len(body)} bytes)")
    print("-" * WIDTH)
    print(body)
    print("*" * WIDTH)
    print()

def create_db(receiver):
    print(receiver.handle_find("A", "1"))
    print(receiver.handle_solve("A", "1", ""))
    print(receiver.handle_solve("A", "1", ""))
    print(receiver.handle_solve("A", "1", "y"))
    
    print(receiver.handle_find("B", "1"))
    
    print(receiver.handle_find("C", "1"))
    print(receiver.handle_solve("C", "1", ""))
    print(receiver.handle_solve("C", "1", "y"))
    
    print(receiver.handle_find("D", "1"))
    print(receiver.handle_solve("D", "1", "y"))
    
    print(receiver.handle_find("A", "2"))
    print(receiver.handle_solve("A", "2", ""))
    print(receiver.handle_solve("A", "2", ""))
    print(receiver.handle_solve("A", "2", "n"))
    
    print(receiver.handle_find("B", "2"))
    print(receiver.handle_solve("B", "2", "n"))

def run():
    version = "0.1"
    path = "test_data.json"
    
    sender = BitboxingSender("B", version)
    receiver = BitboxingReceiver(version, path)
    
    request = sender.handle_solve("1", "q")
    print_request(request)
    
    response = handle_request(request, receiver)
    print(response)
    
    request = sender.handle_stats("B")
    print_request(request)
    
    response = handle_request(request, receiver)
    print(response)
    
if __name__ == "__main__":
    run()
