import argparse
import socket
import shlex
import subprocess
import sys
import threading

def execute_command(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        try:
            if self.args.listen:
                self.listen()
            else:
                self.send()
        except KeyboardInterrupt:
            print("\nUser terminated")
            self.socket.close()
            sys.exit()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response, end='')
                    buffer = input("> ")
                    buffer += "\n"
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("User terminated.")
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f"Listening on {self.args.target}:{self.args.port}")
        while True:
            client_socket, _ = self.socket.accept()
            print(f"Accepted connection from {self.args.target}:{self.args.port}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:
            file_buffer = b""
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                file_buffer += data
            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Saved file {self.args.upload}\n")

        elif self.args.command:
            cmd_buffer = b""
            while True:
                try:
                    client_socket.send(b"<NCC:#> ")
                    while "\n" not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute_command(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b""
                except Exception as e:
                    print(f"Server killed {e}")
                    self.socket.close()
                    sys.exit()

        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Netcat-like tool in Python")
    parser.add_argument("-l", "--listen", action="store_true", help="Listen on [host]:[port] for incoming connections")
    parser.add_argument("-e", "--execute", help="Execute the given command upon receiving a connection")
    parser.add_argument("-c", "--command", action="store_true", help="Initialize a command shell")
    parser.add_argument("-t", "--target", default="127.0.0.1", help="Target host")
    parser.add_argument("-p", "--port", type=int, required=True, help="Target port")
    parser.add_argument("-u", "--upload", help="Upload file")
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()