#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

def simul(init,avg,n):
    """
    Simulates the consumption of a resource, following a poisson process, for a given number of steps
    @params:
        init: float, initial amount of resources
        avg: float, average time for an event to happen
        n: float, amount of steps to simulate
    @return:
        steps: array of steps taken
        amnt: array, gives the amount of resources at any point of the simulation
    """
    steps = [i for i in range(n+1)]
    lamb= 1/avg
    amnt = [init]
    time_til_next = np.random.poisson(lamb)
    for i in range(n):
        time_til_next -=1
        print(time_til_next)
        if(time_til_next = 0):
            amnt.append(amnt[-1] - 1)
            time_til_next = np.random.poisson(lamb)
        else:
            amnt.append(amnt[-1])
    return steps,amnt

avg = 40
init = 10000
st, am = simul(init,avg,20000)
plt.plot(st,am)
plt.show()
