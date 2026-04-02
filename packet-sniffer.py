# This tools needs root/sys admin privileges to run
# Usage: python3 packet-sniffer.py [your machine's IP Addr]

from ctypes import *
import os
import socket
import struct
import sys

# host to listen on
HOST = sys.argv[1]

def parse_ip_header(data):
    # Unpack the first 20 bytes of the IP header
    ip_header = struct.unpack('!BBHHHBBH4s4s', data[:20])
    version_ihl = ip_header[0]
    version     = version_ihl >> 4
    ihl         = (version_ihl & 0xF) * 4  # Header length in bytes
    ttl         = ip_header[5]
    protocol    = ip_header[6]
    src_ip      = socket.inet_ntoa(ip_header[8])
    dst_ip      = socket.inet_ntoa(ip_header[9])
    print(f"{version} {ihl} {ttl} {protocol} {src_ip} {dst_ip}")

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

    print("Version | Header Len | TTL | Protocol | Src IP | Dest IP | Payload")

    # read packets
    while True:
        try:
            packets = sniffer.recvfrom(65565)
            parse_ip_header(packets[0])
            print(packets[0][20:].decode('ascii', errors='ignore'))
            
        except KeyboardInterrupt:
             # if we're on Windows, turn off promiscuous mode
            if os.name == 'nt':
                sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            sys.exit(0)

        except Exception as ex:
            print(f"Error: {ex}")

if __name__ == '__main__':
    main()