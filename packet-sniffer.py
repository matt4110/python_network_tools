# This tools needs root/sys admin privileges to run
# Usage: python3 packet-sniffer.py [your machine's IP Addr]

from ctypes import *
import os
import socket
import struct
import sys

# host to listen on
HOST = sys.argv[1]

def main():
    # Check OS and set appropriate protocol
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # Create raw socket and bind to public interace
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((HOST, 0))

    # include the IP header in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # if we're on Windows, turn on promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # read one packet
    print(sniffer.recvfrom(65565))

    # if we're on Windows, turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == '__main__':
    main()