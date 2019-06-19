#!/usr/bin/python
import multiprocessing as mp
import time

import hub
import client
import actuator
import sensor

h = hub.HUB()
cl = client.Client(0,0)
sensores = [sensor.Sensor(1,1), sensor.Sensor(2,1), sensor.Sensor(3,1)]
atuador = [actuator.Actuator(4,1), actuator.Actuator(5,1), actuator.Actuator(6,1), actuator.Actuator(7,1)]

processes = [mp.Process(target = h.handshake,args = ())]
processes[0].start()
time.sleep(0.5)
#sensores
for s in sensores:
    processes.append(mp.Process(target = s.handshake, args = ()))
    processes[-1].start()
for a in atuador:
    processes.append(mp.Process(target = a.stateShifter, args = ()))
    processes[-1].start()
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
