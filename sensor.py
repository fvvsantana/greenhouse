import socket
import struct
from math import pi

class Sensor:
    def __init__(self, type, serialNumber):
        sensor_type = int.from_bytes(type, "big")
        self.sock = None
        if (sensor_type > 0 and sensor_type < 4):
            if (serialNumber >= 0 and serialNumber < 32):
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
            soc.send(bytes([0]))    

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.255.1',new_port))
        if (self.type == 1): #temp
                self.__threads.append(threading.Thread(target = self.send_loop_temp, args=(len(self.__threads))))
                self.__threads[-1].start()
        elif (self.type == 2): # umid
                self.__threads.append(threading.Thread(target = self.send_loop_temp, args=(len(self.__threads))))
                self.__threads[-1].start()
        elif (self.type == 3): # coo
                self.__threads.append(threading.Thread(target = self.send_loop_temp, args=(len(self.__threads))))
                self.__threads[-1].start()
    
    def send(self, value):
        bytes_to_send = struct.pack("f", value)
        self.send(bytes_to_send)
        

    def send_loop_co2(self, thread_index):
        inc = 0
        while (1):
            self.send((sin((inc*pi)/180.0)+1)*0.5)
            sleep(1.0)
    
    def send_loop_um(self, thread_index):
        inc = 0
        while (1):
            self.send((sin((inc*pi)/180.0)+1) * 50)
            sleep(1.0)
    
    def send_loop_temp(self, thread_index):
        inc = 0
        while (1):
            self.send(((sin((inc*pi)/180.0)+1) * 20)+5)
            sleep(1.0)
        
        
    def close(self):
        self.sock.close()

Sensor(1, 0)