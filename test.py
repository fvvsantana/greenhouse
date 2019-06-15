#!/usr/bin/python
import socket
import struct

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('127.0.255.1',1337))
soc.send(b'\x80')
newp = soc.recv(2)
newp = int.from_bytes(newp, 'big')
soc.send(b'\x01')
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('127.0.255.1',newp))
while(1):
    try:
        rec = soc.recv(1)
        print(rec)
        soc.send(b'\x00')
    except:
        soc.close()
        break
