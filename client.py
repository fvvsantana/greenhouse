#!/usr/bin/python
import struct
import socket
#from main import killProcesses 

class Client:

    def __init__(self, type, serialNumber):

        #concatena o tipo e o numero serial para mandar
        self.type = type
        self.serialNumber = serialNumber
        if type == 0:
            if serialNumber <= 31 and serialNumber >= 0:
                self.__ID = serialNumber
            else:
                raise AttributeError('ERROR: Invalid serial number. Must be between 0 and 31')
        else:
            raise AttributeError('ERROR: Invalid type. Must be between 4 and 7')

        #define os atributos de conexao
        self.__soc = None
        self.__port = 1337
        self.__addr = '127.0.255.1'


    def connect(self):
        #abre a conexao do socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            self.__soc = soc
            soc.connect((self.__addr, self.__port))

            #envia o id
            soc.send(bytes([self.__ID]))

            #pega os dois bytes pra porta
            auxPort = soc.recv(2)

            #se a transmissao falhou
            if len(auxPort) != 2:
                #envia nAck
                soc.send(bytes([0]))
                #fecha conexao
                soc.close()
                raise AttributeError("ERROR: Connection error")
            else:
                #troca os bytes para gerar o numero da porta
                newPort = auxPort[0]<<8 | auxPort[1]
                soc.send(bytes([255]))

        #cria uma nova conexao na nova porta
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__soc.connect((self.__addr, newPort))


    def requestData(self, type, serialNumber):
        #print('Request data')
        self.__soc.send(bytes([type << 5 | serialNumber]))

    def receiveData(self):
        #pega os 5 bytes de tipo e dados
        data = self.__soc.recv(5)
        #pega o tipo (primeiro byte)
        #type = int.from_bytes(data[0], 'big')
        type = data[0]
        #remove o tipo da lista
        data = data[1:]

        #checa se eh uma mensagem de dado ou de erro
        if type == 0: #se for dado
            #converte os dados para float
            data = struct.unpack('f', data)
            #imprime os dados
            print('Data: %f' % data)

        else: #se for erro
            print('Erro de comunicação:\n\tComponente: ', data[-1], '\n\tCódigo: ', data[-2], '\n')
            #print('Erro de comunicação:\n\tComponente: %b\n\tCódigo: %b\n' % data[-1], data[-2])
            #print('Erro de comunicação:\n\tComponente: %d\n\tCódigo: %d\n' % (10, 5))



if __name__ == '__main__':
    #inicia cliente
    client = Client(0, 0)

    #inicia handshake do cliente
    try:
        client.connect()

        while(1):
            operation = input("enter with q to quit, or the ID of the desired sensor: ")
            try:
                ck = int(operation,2)
            except:
                ck = None
            if(not ck): #algo que nao eh um numero binario foi entrado, sai do loop
                break
            else:
                client.requestData(int(operation[:3],2),int(operation[3:],2))
    except Exception as e:
        print(e)
    #finally:
        #killProcesses()
    
