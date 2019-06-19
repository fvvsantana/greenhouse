#!/usr/bin/python
import multiprocessing as mp
import time

import hub
import client

h = hub.HUB()
cl = client.Client(0,0)

processes = [mp.Process(target = h.handshake,args = ())]
processes[-1].start()
time.sleep(0.1)
for p in processes[1:]:
    p.start()
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
