import threading
import socket
import sys

try:
    target = sys.argv[1]
except IndexError:
    print("Usage: python port-scanner.py <target_ip>")
    sys.exit(1)

open_ports = []

ports_to_scan = range(1, 1025)  # Scanning ports from 1 to 1024

def scan_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        if s.connect_ex((target, port)) == 0:
            open_ports.append(port)

threads = []
for port in ports_to_scan:
    t = threading.Thread(target=scan_port, args=(port,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Open TCP ports:", open_ports)