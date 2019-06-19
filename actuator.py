import numpy as np
import socket

"""
Véi, foca no código


        .---.
       /o   o\
    __(=  "  =)__
     //\'-=-'/\\
        )   (_
       /      `"=-._
      /       \     ``"=.
     /  /   \  \         `=..--.
 ___/  /     \  \___      _,  , `\
`-----' `""""`'-----``"""`  \  \_/
                             `-`

""""""

class Actuator:
    def _init_ (self, type, serialNumber):
        self.__sock = None
        self.__port = 1337
        self.__addr = '127.0.255.1'
        self.__socket = socket.socket(socket.AF_NET, socket.SOCK_STREAM)

        self.state = False
        self.type = type
        self.serialNumber = serialNumber

        if type > 3 and type < 8:
            if serialNumber < 32 and serialNumber >= 0:
                self.__ID = type << 5 | serialNumber
            else:
                raise AttributeException("ERROR: Invalid serial number. Must be between 0 to 31")
        else:
            raise AttributeException("ERROR: Invalid type. Must be between 4 to 7")
    '''
        A funcao 'connect' se conecta ao HUB na porta e ip padrao contidos atuador. Ele manda seu ID e espera uma resposta de 2 bytes contendo
        a sua porta exclusiva para se conectar. Caso o pacote recebido nao seja de 2 bytes, ele fecha a comunicacao, manda um codigo
        de erro e termina a execucao do atuador. Em caso de sucesso, o atuador se conecta na porta recebida e a comunicacao/execucao
        do sistema continua
    '''
    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.bind((self.__addr, self.__port))
            soc.connect((self.__addr, self.__port))
            soc.send(bytes([self.ID]))
            auxPort = soc.recv(2)
            if len(auxPort) != 2:
                soc.send(bytes([0]))
                soc.close()
                raise AttributeException("ERROR: Connection error")
            else:
                newPort = auxPort[0] << 8 | auxPort[1]
                soc.send(bytes([255]))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.__addr,  newPort))
        self.sock.connect((self.__addr, newPort))

    def stateShifter(self):
        self.connect(self)
        while 1:
            message = self.sock.recv(2)
            if len(stateShifter) == 2:
                data = message[0] << 8 | message[1]
                if data != 0:
                    self.state = !self.state
                self.sock.send(bytes([255]))
            elif len(stateShifter) == 1:
                data = message[0]
                if data != 0:
                    self.state = !self.state
                self.sock.send(bytes([255]))
            else:
                self.sock.send(bytes([0]))
                self.sock.close()
                raise AttributeException("ERROR: Invalid size of package received at actuator")
