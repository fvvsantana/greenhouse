import socket
import struct

class Sensor:
    def __init__(self, type, serialNumber):
        self.sock = None
        if (type > 0 && type < 4):
            if (serialNumber >= 0 && serialNumber < 32):
                self.serial = type<<5 | serialNumber
            else:
                raise AttributeException("ERROR: Invalid serial number")
        else:
            raise AttributeException("ERROR: Invalid type number")
        
        self.__handshake()
    
    def __handshake(self):
        new_port = 0;
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.connect(('127.0.255.1',1337))
            soc.send(bytes([self.serial]))
            aux_port = soc.recv(2)
            if len(aux_port) != 2:
                raise AttributeException("ERROR: Connection error")
            else:
                new_port = aux_port[0]<<8 | aux_port[1]
            
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.255.1',new_port))
    
    def send(self, value):
        bytes_to_send = struct.pack("f", value)
        self.send(bytes_to_send)
        
    def close(self):
        self.sock.close()