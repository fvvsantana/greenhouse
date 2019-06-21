#!/usr/bin/python
import socket
import random
import struct
import time
import datetime
import threading

#retorna se o ID pertence a um sensor
def is_sensor(ID):
    if(ID[0] == '0'):
        return (ID[1] == '1') or (ID[2] == '1')
    return False

#retorna se o ID pertence a um sensor
def is_client(ID):
    return (ID[0] == '0') and (ID[1] == '0') and (ID[2] == '0')

#retorna se o ID pertence a um sensor
def is_actuator(ID):
    return ID[0] == '1'

class HUB:
    #inicia variaveis da classe
    def __init__(self,timeout = 10):
        #inicia socket tcp
        self.__handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #Endereco do servidor
        self.__host = '127.0.255.1'
        #socket ouve na porta 1337
        self.__handshake_socket.bind((self.__host,1337))
        #tempo para matar conexao
        self.__timeout = timeout
        #socket.setdefaulttimeout(timeout) #TODO
        #hashtable de conexoes e portas para cada componente
        #hashtable com chave ID do componente e valor lista de portas
        self.__connections = {} 
        #as conexoes serao armazenadas como uma tupla (socket, port), para evitar que a mesma porta seja reutilizada
        self.__used_ports = []
        #ultimos valores que os sensores enviaram
        self.__last_values = {} 
        #estado atual dos atuadores
        self.__current_state = {}
        #threads dos dispositivos conectados
        self.__threads = []

    def cleanup(self):
        for key in self.__connections:
            soc = self.__connections[key][0]
            soc.close()
        self.__handshake_socket.close()

    #gera um novo numero de porta
    def gen_new_port(self):
        #O valor aleatorio esta no intervalo [5,255] para ser mais facil para converter e mandar a porta pelo socket
        #e ter um valor maior que 1024
        port = random.randint(5,255)
        #encontra uma porta que nao esta sendo usada
        while(port in self.__used_ports):
            port = random.randint(5,255)
        #adiciona porta na lista
        self.__used_ports.append(port)
        #retorna o numero da porta
        return port

    def close_socket(self, ID):
        if(ID not in self.__connections.keys()):
            return
        soc,port = self.__connections[ID]
        self.__used_ports.remove(port)
        soc.close()
        del self.__connections[ID]

    #cria um socket, coloca-o numa lista e adiciona na hashtable __connections
    def create_socket(self, ID, port):
        #cria um socket pra porta port, coloca-o numa lista
        # e a coloca como valor da chave ID
        self.__connections[ID] = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),port]
        #faz o socket ouvir na porta port
        self.__connections[ID][0].bind((self.__host,port))

    def handshake(self):
        #No maximo um de cada componente pode estar esperando na fila
        self.__handshake_socket.listen(7)
        while True:
            #gera um socket que aceita conexoes
            conn, addr = self.__handshake_socket.accept()
            #recebe ID de um componente conectando
            ID = conn.recv(64)
            if len(ID) > 10:
                raise RuntimeError("Too much data")
                continue
            #transforma id numa string de bytes que sera usada como chave
            ID = format(int.from_bytes(ID,'big'),'08b')
            #caso uma conexao com esse ID ja exista, ela sera fechada
            self.close_socket(ID)
            #inicia uma nova conexao
            #gera nova porta
            new_port = self.gen_new_port()
            #cria o socket com a porta * 256, para ficar acima de 1024
            self.create_socket(ID,new_port*256)
            #TODO não entendi como connections ja tem a conexao nesse ponto do codigo
            self.__connections[ID][0].listen(0)
            #formata id e manda para o dispositivo que se conectou
            data_send = bytes([new_port,0])
            conn.send(data_send)
            #pega o ack do componente
            ack = conn.recv(1)
            #se deu errado, ou seja, eh um nACK
            if(len(ack) == 0 or ack == b'\x00'):
                #fecha conexao
                self.close_socket(ID)
            else:
                #passa a aceitar conexoes na nova porta
                self.__connections[ID][0], _ = self.__connections[ID][0].accept()
                #inicia uma thread, que vai receber ou enviar os dados
                #se for sensor
                if(is_sensor(ID)):
                    #ultimo valor lido recebe -1
                    self.__last_values[ID] = -1
                    #cria uma thread pro sensor
                    self.__threads.append(threading.Thread(target = self.get_data_from_sensor, args=(ID,len(self.__threads))))
                    #inicia a thread
                    self.__threads[-1].start()
                #se for cliente
                elif(is_client(ID)):
                    #cria uma thread para o cliente
                    self.__threads.append(threading.Thread(target = self.interact_with_client, args=(ID,len(self.__threads))))
                    #inicia a thread
                    self.__threads[-1].start()
                #se for atuador
                elif(is_actuator(ID)):
                    #armazena estado do atuador
                    self.__current_state[ID] = [b'\x00',b'\x00']
                    #cria uma thread para o atuador
                    self.__threads.append(threading.Thread(target = self.send_data_to_sensor, args=(ID,len(self.__threads))))
                    #inicia a thread
                    self.__threads[-1].start()
    
    def get_data_from_sensor(self, ID, thread_index):
        while(1):
            data = self.__connections[ID][0].recv(4) #4 bytes que serao interpretados como um float
            if(len(data)):
                self.__connections[ID][0].settimeout(self.__timeout)
                data = struct.unpack('f',data)
                self.__last_values[ID] = data
            else:
                del self.__threads[thread_index]
                self.close_socket(ID)
                break

    #interacao com o cliente, roda numa thread
    def interact_with_client(self,ID,thread_index):
        while(1):
            #pega requisicao
            request = self.__connections[ID][0].recv(1) #pacote do tipo 2
            #se deu erro
            if(len(request) == 0):
                #fecha a conexao
                self.close_socket(ID)
                del self.__threads[thread_index]
                #TODO falta um return aqui? pq a thread nao eh pra ser mais executada
            #se o cliente mandou um keep alive
            elif(request == b'\x00'):
                #so mandado para a conexao nao morrer
                to_send = bytes(5)
                self.__connections[ID][0].sendall(to_send)
            else:
                req = int.from_bytes(request, 'big')
                req = '{0:b}'.format(req)
                #se pediu um sensor
                if(req[0] == '0'):
                    tp = b'\x00'
                    #se a media entre sensores foi requisitada
                    if(req[3:] == '00000'):
                        vals = []
                        for key in self.__last_values:
                            if(req[:3] == key[:3]):
                                vals.append(self.__last_values[key])
                        try:
                            val = sum(vals)/len(vals)
                        except:
                            val = 0.0
                            tp = b'\x01'
                    #senao, entrega o ultimo valor lido do sensor
                    else:
                        try:
                            val = self.__last_values[req]
                        except:
                            val = 0.0
                            tp = b'\x01'
                #se pediu um atuador
                else:
                    try:
                        val = self.__current_state[req][0]
                        tp = b'\x00'
                    except:
                        val = 0.0
                        tp = b'\x01'
                #envia float de dados
                to_send = tp + struct.pack('f',val)
                self.__connections[ID][0].sendall(to_send)

    def send_data_to_sensor(self, ID, thread_index):
        time_til_heartbeat = datetime.datetime.now() + datetime.timedelta(seconds = self.__timeout)
        while(1):
            #check if a new command should be issued
            if(self.__current_state[ID][0] != self.__current_state[ID][1]):
                self.__current_state[ID][0] = self.__current_state[ID][1]
                self.__connections[ID][0].send(self.__current_state[ID][0])
                data = self.__connections[ID][0].recv(1)
                if(len(data) == 0):
                    #o sensor foi desconectado, precisa avisar o cliente
                    print('a')
                    self.close_socket(ID)
                    del self.__threads[thread_index]
                    break
                elif(data != b'\x00'):
                    #aconteceu um erro precisa mandar para o cliente
                    print('b')
                    self.close_socket(ID)
                    del self.__threads[thread_index]
                    break
                else:
                    #do contrario, tudo certo, calculamos um novo momento para manter a conexao viva
                    time_til_heartbeat = datetime.datetime.now() + datetime.timedelta(seconds = self.__timeout)
            #wait for data/timeout
            elif(time_til_heartbeat <= datetime.datetime.now()):
                self.__connections[ID][0].send(self.__current_state[ID][0])
                data = self.__connections[ID][0].recv(1)
                if(len(data) == 0):
                    #o sensor foi desconectado, precisa avisar o cliente
                    self.close_socket(ID)
                    del self.__threads[thread_index]
                    break
                elif(data != b'\x00'):
                    #aconteceu um erro precisa mandar para o cliente
                    self.close_socket(ID)
                    del self.__threads[thread_index]
                    break
                else:
                    #do contrario, tudo certo, calculamos um novo tempo para o heartbeat
                    time_til_heartbeat = datetime.datetime.now() + datetime.timedelta(seconds = self.__timeout)
            time.sleep(0.3)


#TODO
if __name__ == '__main__':
    hub = HUB()
    hub.handshake()
    """
    try:
        hub.handshake()
    except Exception as e:
        print('erro',e)
    finally:
        hub.cleanup()
    """
