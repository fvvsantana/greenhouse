#!/usr/bin/python
import socket
import struct

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('127.0.255.1',1337))
soc.send(b'\x60')
newp = soc.recv(2)
newp = int.from_bytes(newp, 'big')
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('127.0.255.1',newp))
to_send = struct.pack('f',3.141598)
soc.send(to_send)
