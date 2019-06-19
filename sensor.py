import socket
import struct
import threading
from math import pi, sin
from time import sleep

class Sensor:
    def __init__(self, type, serialNumber):
        sensor_type = type
        self.type = type
        self.sock = None
        if (sensor_type > 0 and sensor_type < 4):
            if (serialNumber >= 0 and serialNumber < 32):
                self.serial = type<<5 | serialNumber
            else:
                raise AttributeException("ERROR: Invalid serial number")
        else:
            raise AttributeException("ERROR: Invalid type number")
        
    
    def handshake(self):
        new_port = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.connect(('127.0.255.1',1337))
            soc.send(bytes([self.serial]))
            aux_port = soc.recv(2)
            if len(aux_port) != 2:
                raise AttributeException("ERROR: Connection error")
            else:
                new_port = aux_port[0]<<8 | aux_port[1]
            soc.send(bytes([1]))    

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.255.1',new_port))
        if (self.type == 1): #temp
                threading.Thread(target = self.send_loop_temp, args = ()).start()
        elif (self.type == 2): # umid
                threading.Thread(target = self.send_loop_um, args=()).start()
        elif (self.type == 3): # coo
                threading.Thread(target = self.send_loop_co2, args=()).start()
    
    def send(self, value):
        bytes_to_send = struct.pack("f", value)
        self.sock.sendall(bytes_to_send)
        

    def send_loop_co2(self):
        inc = 0
        while (1):
            self.send((sin((inc*pi)/180.0)+1)*0.5)
            inc += 1
            sleep(1.0)
    
    def send_loop_um(self):
        inc = 0
        while (1):
            self.send((sin((inc*pi)/180.0)+1) * 0.5)
            inc += 1
            sleep(1.0)
    
    def send_loop_temp(self):
        inc = 0
        while (1):
            self.send(((sin((inc*pi)/180.0)+1) * 20)+5)
            inc += 1
            sleep(1.0)
        
        
    def close(self):
        self.sock.close()

Sensor(1, 0)
