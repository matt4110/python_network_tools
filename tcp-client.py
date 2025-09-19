import socket
import sys

# Get target IP and port from command line arguments
try:
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
except IndexError:
    print("Usage: python script.py <target_ip> <target_port>")
    sys.exit(1)
except ValueError:
    print("Invalid port number.")
    sys.exit(1)

# Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((target_ip, target_port))
print(f"[[CONNECTED: {target_ip}:{target_port}]]")

# Communication loop
try:
    while True:
        message = input("[[SEND]]: ")
        if message.lower() == 'quit':
            s.send(str.encode("[[CLOSING CONNECTION]]"))
            break
        s.send(str.encode(message))
        received = s.recv(1024).decode()
        print(f"[[RECEIVED]]: {received}")
except KeyboardInterrupt:
    print("\n[[CLOSING CONNECTION]]")

s.close()