#!/usr/bin/python
import socket
import random

class HUB:
    def __init__(self,timeout = 10):
        self.__handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__host = '127.0.255.1'
        self.__handshake_socket.bind((self.__host,1337))
        socket.setdefaulttimeout(timeout)
        self.__connections = {} #hashtable de conexoes e portas para cada componente
        #as coneccoes serao armazenadas como uma tupla (socket,port), para evitar que a mesma porta seja reutilizada
        self.__used_ports = []

    def cleanup(self):
        for key in self.__connections:
            soc = self.__connections[key][0]
            soc.close()
        self.__handshake_socket.close()

    def gen_new_port(self):
        #O valor aleatorio esta no intervalo [0,255] para ser masi facil para converter e mandar a porta pelo socket
        port = random.randint(5,255)
        while(port in self.__used_ports):
            port = random.randint(5,255)
        self.__used_ports.append(port)
        return port

    def close_socket(self, ID):
        if(ID not in self.__connections.keys()):
            return
        soc,port = self.__connections[ID]
        self.__used_ports.remove(port)
        soc.close()

    def create_socket(self, ID, port):
        self.__connections[ID] = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),port]
        self.__used_ports.append(port)
        self.__connections[ID][0].bind((self.__host,port))

    def handshake(self):
        self.__handshake_socket.listen(7) #No maximo um de cada componente pode estar esperando na fila
        while True:
            conn, addr = self.__handshake_socket.accept()
            ID = conn.recv(64) #ID do componente conectando
            if len(ID) > 10:
                raise RuntimeError("Too much data")
                continue
            ID = format(int.from_bytes(ID,'big'),'08b')
            #caso uma conecao com esse ID ja existisse, ela sera fechada
            self.close_socket(ID)
            #inicia uma nova conexao
            #gera nova porta
            new_port = self.gen_new_port()
            #cria a socket
            self.create_socket(ID,new_port*256)
            self.__connections[ID][0].listen(0)
            #formata para mandar
            data_send = bytes([new_port,0])
            print(data_send)
            conn.send(data_send)
            print(data_send)
            ack = conn.recv(1)
            if(len(ack) == 0 or ack == b'\x00'):
                self.close_socket(ID)
            else:
                self.__connections[ID][0].accept()



if __name__ == '__main__':
    hub = HUB()
    try:
        hub.handshake()
    except Exception as e:
        print(e)
    finally:
        hub.cleanup()
