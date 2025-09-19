from datetime import datetime
import socket
import sys

now = datetime.now()
timestamp = now.strftime("%Y.%m.%d %H:%M")

try:
    listen_port = int(sys.argv[1])
except (IndexError, ValueError):
    print("Usage: python script.py <listen_port>")
    sys.exit(1)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", listen_port))
s.listen(5)

conn = False

while True:
    try:
        if conn is False:
            print(f"[[LISTENING ON PORT {listen_port}]]")
            conn, client = s.accept()
            print(f"[[CONNECTED: {client[0]}:{client[1]}]]")

        received = conn.recv(1024).decode("utf-8")
        print(f"[[RECEIVED]]: {received}")
        with open("tcp-server.txt", "a") as file:
            file.write(f"\n>>>>>>\n{timestamp} \n{client[0]}:{client[1]} \n{received}\n\n")
        conn.send(str.encode(f"Message received at {timestamp}"))
    except KeyboardInterrupt:
        print("[[CLOSING CONNECTION]]")
        conn.close()
        break
    except BrokenPipeError:
        print("[[CONNECTION LOST]]")
        conn = False

s.close()