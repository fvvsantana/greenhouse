#!/usr/bin/python
import multiprocessing as mp
import time
from utils import ComponentCode as cc

import hub
import actuator
import sensor
import monitor


if __name__ == '__main__':
    #inicializa hub e componentes
    h = hub.HUB()
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

    mon = monitor.Monitor()
    mon.showInfo()

'''

def killProcesses():
    for p in processes:
        p.kill()

'''

