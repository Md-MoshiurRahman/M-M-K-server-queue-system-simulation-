"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
import matplotlib.pyplot as plt
import numpy as py
INF = 99999

# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k

    def returnValue(self):
        value = []
        value.append(self.lambd)
        value.append(self.mu)
        value.append(self.k)
        return value

    def printAnalyticResults(self):
        avgQlength = (self.lambd * self.lambd) / (self.mu * (self.mu - self.lambd))
        avgQdelay = self.lambd / (self.mu * (self.mu - self.lambd))
        util = self.lambd / self.mu

        print('\nMMk Analytic Results: ')
        print('MMk Average queue length: %lf' % (avgQlength))
        print('MMk Average customer delay in queue: %lf' % (avgQdelay))
        print('MMk Time-average server utility: %lf' % (util))

    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

class States:
    def __init__(self):
        # States
        #self.queue = []
        # Declare other states variables that might be needed

        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0

    def update(self, util, avgQdelay, avgQlength, served):
        self.util = util
        self.avgQdelay = avgQdelay
        self.avgQlength = avgQlength
        self.served = served

    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)

class Simulator:
    def __init__(self):
        self.eventQ = []
        self.queue = []
        self.simclock = 0.0
        self.params = None
        self.states = None
        self.arrival = []
        self.service = []
        self.serviceBackup = []
        self.serverState = 0
        self.numInQ = 0
        self.totalservertime = 0
        self.totalServed = 0
        self.count = 0
        self.maxCount = 0
        self.numInQChecker = 0
        self.numInQTimer = 0
        self.Qlength = 0
        self.Qdelay = 0

    def initialize(self):
        #self.simclock = 0
        self.scheduleEvent()

    def configure(self, params, states, maxCount):
        self.params = params
        self.states = states
        self.maxCount = maxCount

    def now(self):
        return self.simclock

    def scheduleEvent(self):

        value = self.params.returnValue()
        lambd = value[0]
        mu = value[1]

        randArrival = py.random.exponential(1/lambd, self.maxCount)
        randService = py.random.exponential(1/mu, self.maxCount)

        self.arrival = randArrival.tolist()
        self.service = randService.tolist()
        self.serviceBackup = randService.tolist()

        arr = self.arrival.pop(0)
        type = 'Arrival'

        self.eventQ.append([arr,type])


    def run(self):
        self.initialize()
        print(self.simclock, " ", "Start")

        while len(self.eventQ) > 0 :

            self.count += 1

            ind = self.eventQ.index(min(self.eventQ))
            eventtime, eventtype = self.eventQ.pop(ind)
            self.simclock = eventtime

            print(eventtime, " ", eventtype)


            if eventtype == 'Arrival' :
                if self.serverState == 0 :
                    self.serverState = 1

                    #############add next depart##########
                    dep = self.service.pop(0) + self.simclock
                    type = 'Departure'
                    self.eventQ.append([dep, type])
                else :
                    self.numInQ = self.numInQ + 1
                    self.queue.append(self.simclock)

               ##########add next arrival#########
                arr = self.arrival.pop(0) + self.simclock
                type = 'Arrival'
                self.eventQ.append([arr, type])



            if eventtype == "Departure" :
                self.totalServed += 1

                if self.numInQ == 0 :
                    self.serverState = 0
                else:
                    self.numInQ = self.numInQ - 1
                    self.Qdelay += self.simclock - self.queue.pop(0)

                    #############add next depart##########
                    dep = self.service.pop(0) + self.simclock
                    type = 'Departure'
                    self.eventQ.append([dep, type])

            if self.numInQ != self.numInQChecker :
                self.Qlength += (self.simclock - self.numInQTimer) * self.numInQChecker
                self.numInQTimer = self.simclock
                self.numInQChecker = self.numInQ

            print('Server ', self.serverState, ', ', 'Queue ', self.numInQ, '\n')

            if self.count == self.maxCount :     ##########run will stop here###########
                i = 0
                while i < self.totalServed :
                    self.totalservertime += self.serviceBackup[i]
                    i += 1

                util = self.totalservertime / self.simclock
                avgQlength = self.Qlength / self.simclock
                avgQdelay = self.Qdelay / self.totalServed

                self.states.update(util, avgQdelay, avgQlength, self.totalServed)

                #print('Util',util)
                #print('AvgQLength',avgQlength)
                #print('AvgQDelay',avgQdelay)
                #print('TotalServed',self.totalServed)

                break

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


def experiment1():
    maxCount = 10000
    sim = Simulator()
    states = States()
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1), states, maxCount)
    sim.run()
    sim.printResults()

    sim.params.printAnalyticResults()


def main():
    experiment1()


if __name__ == "__main__":
    main()