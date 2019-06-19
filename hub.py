#!/usr/bin/python
import socket
import random
import struct
import time
import datetime
import threading

def is_sensor(ID):
    if(ID[0] == '0'):
        return (ID[1] == '1') or (ID[2] == '1')
    return False

def is_client(ID):
    return (ID[0] == '0') and (ID[1] == '0') and (ID[2] == '0')

def is_actuator(ID):
    return ID[0] == '1'

class HUB:
    def __init__(self,timeout = 10):
        self.__handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__host = '127.0.255.1'
        self.__handshake_socket.bind((self.__host,1337))
        self.__timeout = timeout
        #socket.setdefaulttimeout(timeout)
        self.__connections = {} #hashtable de conexoes e portas para cada componente
        #as coneccoes serao armazenadas como uma tupla (socket,port), para evitar que a mesma porta seja reutilizada
        self.__used_ports = []
        self.__last_values = {} #ultimo valor que o sensor enviou
        self.__current_state = {} #estado atual do atuador
        self.__threads = []

    def cleanup(self):
        for key in self.__connections:
            soc = self.__connections[key][0]
            soc.close()
        self.__handshake_socket.close()

    def gen_new_port(self):
        #O valor aleatorio esta no intervalo [5,255] para ser mais facil para converter e mandar a porta pelo socket
        #e ter um valor maior que 1024
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
        del self.__connections[ID]

    def create_socket(self, ID, port):
        self.__connections[ID] = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),port]
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
            conn.send(data_send)
            ack = conn.recv(1)
            if(len(ack) == 0 or ack == b'\x00'):
                self.close_socket(ID)
            else:
                self.__connections[ID][0], _ = self.__connections[ID][0].accept()
                #inicia uma thread, que vai receber ou enviar os dados
                if(is_sensor(ID)):
                    self.__last_values[ID] = -1
                    self.__threads.append(threading.Thread(target = self.get_data_from_sensor, args=(ID,len(self.__threads))))
                    self.__threads[-1].start()
                elif(is_client(ID)):
                    self.__threads.append(threading.Thread(target = self.interact_with_client, args=(ID,len(self.__threads))))
                    self.__threads[-1].start()
                elif(is_actuator(ID)):
                    self.__current_state[ID] = [b'\x00',b'\x00']
                    self.__threads.append(threading.Thread(target = self.send_data_to_sensor, args=(ID,len(self.__threads))))
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

    def interact_with_client(self,ID,thread_index):
        while(1):
            request = self.__connections[ID][0].recv(1) #pacote do tipo 2
            if(len(request) == 0):
                self.close_socket(ID)
                del self.__threads[thread_index]
            elif(request == b'\x00'):
                #so mandado para a conexao nao morrer
                to_send = bytes(5)
                self.__connections[ID][0].sendall(to_send)
            else:
                req = int.from_bytes(request, 'big')
                req = '{0:b}'.format(req)
                if(req[0] == '0'):
                    tp = b'\x00'
                    if(req[3:] == '00000'):
                        #a media entre sensores foi requisitada
                        vals = []
                        for key in self.__last_values:
                            if(req[:3] == key[:3]):
                                vals.append(self.__last_values[key])
                        try:
                            val = sum(vals)/len(vals)
                        except:
                            val = 0.0
                            tp = b'\x01'
                    else:
                        try:
                            val = self.__last_values[req]
                        except:
                            val = 0.0
                            tp = b'\x01'
                else:
                    try:
                        val = self.__current_state[req][0]
                        tp = b'\x00'
                    except:
                        val = 0.0
                        tp = b'\x01'
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
