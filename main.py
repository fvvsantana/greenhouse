#!/usr/bin/python
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

    while(1):
        op = input("enter with q to quit, or the ID of the desired sensor: ")
        try:
            ck = int(op,2)
        except:
            ck = None
        if(not ck): #algo que nao eh um numero binario foi entrado, sai do loop
            break
        else:
            cl.requestData(int(op[:3],2),int(op[3:],2))
except Exception as e:
    print(e)
finally:
    for p in processes:
        p.kill()
