import socket

class Client:

	def __init__(self, type, serialNumber):

		#concatena o tipo e o numero serial para mandar
		self.type = type
		self.serialNumber = serialNumber
		if type != 0:
			if serialNumber <= 31 and serialNumber >= 0:
				self.__ID = serialNumber
			else:
				raise AttributeException('ERROR: Invalid serial number. Must be between 0 and 31')
		else:
			raise AttributeException('ERROR: Invalid type. Must be between 4 and 7')

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
	            raise AttributeException("ERROR: Connection error")
	        else:
	        	#troca os bytes para gerar o numero da porta
	            newPort = auxPort[0]<<8 | auxPort[1]
				soc.send(bytes([255]))

		#cria uma nova conexao na nova porta
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.__addr, newPort))

