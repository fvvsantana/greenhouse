import socket

class HUB:
    def __init__(self,porta):
        self.__handshake_socket = socket.socket(AF_INET)
        self.__porta = porta
        self.__handshake_socket.bind(('127.0.255.1',1337))
