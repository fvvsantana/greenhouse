#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

def gaussian_curve(x,sigma,mu):
    return np.exp(-(x - mu)**2/(2*sigma**2))/(sigma * np.sqrt(2*np.pi))

def prob(temp,mu,sigma):
    """
    Calculate de probabilities for a given temperature jump, given the probability distribution
    @params:
        temp: float, current temperature
        mu: float, average temperature
        sigma: float, standard deviation
    @return
        np.array: probabilities of the jump from current temperature
    """
    max_jump = 5
    dists = np.linspace(-2,+2,2*max_jump) #linspace size must be even
    #ind = dists.index(0)
    #dists[ind] = 1
    y = gaussian_curve(dists + temp, sigma, mu)
    probs = np.abs(y / dists)
    #inserts 0 with complimentar probability
    prob_tot = sum(probs)
    #normalize probabilities
    probs = probs/prob_tot
    return dists,probs

def jump_prob(temp, mu, sigma):
    """
    Calculate the probability that the temperature will jump, given the probability distribution.
    The minimum probabilty is 10%, the maximum is 90%. these aren't necessarily realistic, but they'll add spice to simultaion
    @params:
        temp: float, current temperature
        mu: float, average temperature
        sigma: float, standard deviation
    """
    dif = np.abs(temp - mu) / sigma
    if(dif > 3):
        #if the temperature is above 3 times stddev, caps the probability at 90%
        dif = 3.0
    return 0.1 + 0.8*dif/3

def simulate(init, mu, sigma, n=100):
    """
    Simulates the temperature system with n steps
    @params:
        init: float, initial temperature
        mu: average temperature
        sigma: standard deviation
        n: int, amount of steps
    @return:
        step: array, the step number, goes from 0 to n, inclusive
        temps: array, the temperature in each step
    """
    steps = [i for i in range(n+1)]
    temps = [init]
    randoms = np.random.rand(n,2)
    for i in range(n):
        curr_temp = temps[-1]
        r = randoms[i]
        jmp = jump_prob(curr_temp, mu, sigma)
        if(r[0] < jmp):
            dist,probs = prob(curr_temp, mu,sigma)
            r = r[1]
            for i,p in enumerate(probs):
                print(r,p)
                r -= p
                if(r <= 0):
                    curr_temp += dist[i]
                    break
        temps.append(curr_temp)
    return steps,temps

if __name__ == '__main__':
    mu = 27
    sigma = 0.5
    steps, temps = simulate(27,mu,sigma,1000)
    plt.plot(steps,temps)
    plt.xlabel('tempo (s)')
    plt.ylabel('temperatura (C)')
    plt.savefig('simul')
