#!/usr/bin/python
import os
import multiprocessing as mp
import time
from client import ComponentCode as cc

import hub
import client
import actuator
import sensor

#inicializa hub e componentes
h = hub.HUB()
cl = client.Client(0,0)
sensores = [sensor.Sensor(cc.temperature_sensor.value,1),
            sensor.Sensor(cc.humidity_sensor.value,1),
            sensor.Sensor(cc.co2_sensor.value,1)]
atuador = [actuator.Actuator(cc.heater.value,1),
            actuator.Actuator(cc.cooler.value,1), 
            actuator.Actuator(cc.irrigator.value,1), 
            actuator.Actuator(cc.co2_injector.value,1)]

#inicia handshake do hub e espera meio segundo
processes = [mp.Process(target = h.handshake,args = ())]
processes[0].start()
time.sleep(0.5)

#inicia handshake dos sensores
for s in sensores:
    processes.append(mp.Process(target = s.handshake, args = ()))
    processes[-1].start()

#inicia handshake dos atuadores
for a in atuador:
    processes.append(mp.Process(target = a.stateShifter, args = ()))
    processes[-1].start()

#inicia handshake do cliente
try:
    cl.connect()
    
    #colocar esse clear a mais se tiver excecoes aparecendo
    #os.system('clear')

    while(1):

        option = input("Digite alguma das opcoes abaixo:\n\
                    \tt: temperatura\n\
                    \tu: umidade\n\
                    \tc: co2\n\n")
                    #\tm: media\n\n")
        os.system('clear')
        valid = True
        if option == 't':
            operation = '00100001'
            print('Temperatura: ', end = '')
        elif option == 'u':
            operation = '01000001'
            print('Umidade: ', end = '')
        elif option == 'c':
            operation = '01100001'
            print('Nivel de CO2: ', end = '')
            '''
        elif option == 'm':
            operation = '00100000'
            print('Media: ', end = '')
            '''
        else:
            valid = False

        if valid:
            cl.requestData(int(operation[:3],2),int(operation[3:],2))
            cl.receiveData()
        else:
            print('Invalid option')

except Exception as e:
    print(e)
finally:
    for p in processes:
        p.kill()


        '''
        try:
            ck = int(op,2)
        except:
            ck = None
        if(not ck): #algo que nao eh um numero binario foi entrado, sai do loop
            print('Not valid ID')
            break
            '''


