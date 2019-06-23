import socket
import struct
import threading
from math import pi, sin
from time import sleep

class Sensor:
    def __init__(self, type, serialNumber): # Ao criar o objeto seta o basico das variaveis
        sensor_type = type
        self.type = type
        self.sock = None
        if (sensor_type > 0 and sensor_type < 4):  # Verifica se os valores são validos
            if (serialNumber >= 0 and serialNumber < 32):
                self.serial = type<<5 | serialNumber
            else:
                raise AttributeException("ERROR: Invalid serial number")
        else:
            raise AttributeException("ERROR: Invalid type number")
        
    
    def handshake(self): # Realiza o handshake para montar a conexao
        new_port = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc: # Começa uma conexao padrao para 
            soc.connect(('127.0.255.1',1337))                           # pegar a porta da conexao definitiva
            soc.send(bytes([self.serial]))
            aux_port = soc.recv(2)
            if len(aux_port) != 2:
                raise AttributeException("ERROR: Connection error")
            else:
                new_port = aux_port[0]<<8 | aux_port[1]
            soc.send(bytes([1]))    

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Comeca a conexao definitiva
        self.sock.connect(('127.0.255.1',new_port)) 
        # Chama o loop de gerar os valores do sensor
        if (self.type == 1): #temp
                threading.Thread(target = self.send_loop_temp, args = ()).start()
        elif (self.type == 2): # umid
                threading.Thread(target = self.send_loop_um, args=()).start()
        elif (self.type == 3): # coo
                threading.Thread(target = self.send_loop_co2, args=()).start()
    
    def send(self, value): # Manda os valores pela conexao ja estabelecida
        bytes_to_send = struct.pack("f", value)
        self.sock.sendall(bytes_to_send)
        

    def send_loop_co2(self): # Loop de gerar os valores do sensor de CO2
        inc = 0
        while (1):
            self.send((sin((inc*pi)/180.0)+1)*0.5)
            inc += 1
            sleep(1.0)
    
    def send_loop_um(self): # Loop de gerar os valores do sensor de umidade
        inc = 0
        while (1):
            self.send((sin((inc*pi)/180.0)+1) * 0.5)
            inc += 1
            sleep(1.0)
    
    def send_loop_temp(self): # Loop de gerar os valores do sensor de temperatura
        inc = 0
        while (1):
            self.send(((sin((inc*pi)/180.0)+1) * 20)+5)
            inc += 1
            sleep(1.0)
        
        
    def close(self): # Fecha o conexao
        self.sock.close()

