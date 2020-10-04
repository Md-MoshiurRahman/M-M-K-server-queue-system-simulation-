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
        self.serverState = []
        self.numBgServer = 0
        self.numOfServer = 0
        self.numOfCusInQ = []
        self.totalservertime = 0
        self.totalServed = 0
        self.count = 0
        self.maxCount = 0
        self.numInQChecker = []
        self.numInQTimer = 0
        self.Qlength = []
        self.Qdelay = 0
        self.avgQlengthofEach = []

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
        k = value[2]
        self.numOfServer = k

        i = 0
        while i < k:
            innerQ = []
            self.queue.append(innerQ)
            self.numOfCusInQ.append(0.0)
            self.serverState.append(0.0)
            self.numInQChecker.append(0.0)
            self.Qlength.append(0.0)
            i += 1


        randArrival = py.random.exponential(1/lambd, self.maxCount)
        randService = py.random.exponential(1/mu, self.maxCount)

        self.arrival = randArrival.tolist()
        self.service = randService.tolist()
        self.serviceBackup = randService.tolist()

        arr = self.arrival.pop(0)
        type = 'Arrival'
        serverNo = 0

        self.eventQ.append([arr,type,serverNo])


    def run(self):
        self.initialize()
        print(self.simclock, " ", "Start")

        while len(self.eventQ) > 0 :

            self.count += 1

            ind = self.eventQ.index(min(self.eventQ))
            eventtime, eventtype, serverNo = self.eventQ.pop(ind)
            self.simclock = eventtime

            #print(eventtime, " ", eventtype, " ", serverNo)


            if eventtype == 'Arrival' :
                if (self.serverState[serverNo] == 0):
                    self.serverState[serverNo] = 1
                    self.numBgServer += 1

                    #############add next depart##########
                    dep = self.service.pop(0) + self.simclock
                    type = 'Departure'
                    self.eventQ.append([dep, type, serverNo])

                else :
                    self.queue[serverNo].append(self.simclock)
                    self.numOfCusInQ[serverNo] += 1

               ##########add next arrival#########
                arr = self.arrival.pop(0) + self.simclock
                type = 'Arrival'
                freeServer = -1

                if (min(self.serverState) == 0):
                    freeServer = self.serverState.index(min(self.serverState))
                else:
                    freeServer = self.numOfCusInQ.index(min(self.numOfCusInQ))

                self.eventQ.append([arr, type, freeServer])

            if eventtype == "Departure" :
                self.totalServed += 1

                if self.numOfCusInQ[serverNo] == 0:
                    self.serverState[serverNo] = 0
                    self.numBgServer -= 1

                else:
                    self.numOfCusInQ[serverNo] -= 1
                    self.numInQTimer = self.queue[serverNo].pop(0)
                    self.Qdelay += self.simclock - self.numInQTimer

                    #############add next depart##########
                    dep = self.service.pop(0) + self.simclock
                    type = 'Departure'
                    self.eventQ.append([dep, type, serverNo])

                #######(LF – L) or (LR – L)>= 2 part######
                if self.numOfServer > 1:
                    if serverNo == 0:
                        if (self.numOfCusInQ[serverNo + 1] - self.numOfCusInQ[serverNo]) >= 2:
                            fromOther = self.queue[serverNo + 1].pop(-1)
                            self.numOfCusInQ[serverNo + 1] -= 1

                            if (self.serverState[serverNo] == 0):
                                self.serverState[serverNo] = 1
                                self.numBgServer += 1
                                self.Qdelay += self.simclock - fromOther

                                #############add next depart##########
                                #dep = self.service.pop(0) + self.simclock  #######
                                #type = 'Departure'
                                #self.eventQ.append([dep, type, serverNo])

                            else:
                                self.queue[serverNo].append(fromOther)
                                self.numOfCusInQ[serverNo] += 1

                    elif serverNo == (self.numOfServer - 1):
                        if (self.numOfCusInQ[serverNo - 1] - self.numOfCusInQ[serverNo]) >= 2:
                            fromOther = self.queue[serverNo - 1].pop(-1)
                            self.numOfCusInQ[serverNo - 1] -= 1

                            if (self.serverState[serverNo] == 0):
                                self.serverState[serverNo] = 1
                                self.numBgServer += 1
                                self.Qdelay += self.simclock - fromOther

                                #############add next depart##########
                                # dep = self.service.pop(0) + self.simclock  #######
                                # type = 'Departure'
                                # self.eventQ.append([dep, type, serverNo])

                            else:
                                self.queue[serverNo].append(fromOther)
                                self.numOfCusInQ[serverNo] += 1
                    else:
                        if (self.numOfCusInQ[serverNo + 1] - self.numOfCusInQ[serverNo]) >= 2:
                            fromOther = self.queue[serverNo + 1].pop(-1)
                            self.numOfCusInQ[serverNo + 1] -= 1

                            if (self.serverState[serverNo] == 0):
                                self.serverState[serverNo] = 1
                                self.numBgServer += 1
                                self.Qdelay += self.simclock - fromOther

                                #############add next depart##########
                                # dep = self.service.pop(0) + self.simclock  #######
                                # type = 'Departure'
                                # self.eventQ.append([dep, type, serverNo])

                            else:
                                self.queue[serverNo].append(fromOther)
                                self.numOfCusInQ[serverNo] += 1
                        elif (self.numOfCusInQ[serverNo - 1] - self.numOfCusInQ[serverNo]) >= 2:
                            fromOther = self.queue[serverNo - 1].pop(-1)
                            self.numOfCusInQ[serverNo - 1] -= 1

                            if (self.serverState[serverNo] == 0):
                                self.serverState[serverNo] = 1
                                self.numBgServer += 1
                                self.Qdelay += self.simclock - fromOther

                                #############add next depart##########
                                # dep = self.service.pop(0) + self.simclock  #######
                                # type = 'Departure'
                                # self.eventQ.append([dep, type, serverNo])

                            else:
                                self.queue[serverNo].append(fromOther)
                                self.numOfCusInQ[serverNo] += 1
                        else:
                            pass
                #######End of (LF – L) or (LR – L)>= 2 part######

            if self.numOfCusInQ[serverNo] != self.numInQChecker[serverNo] :
                self.Qlength[serverNo] += (self.simclock - self.numInQTimer) * self.numInQChecker[serverNo]
                self.numInQChecker[serverNo] = self.numOfCusInQ[serverNo]

            #print('Server ', self.serverState, ', ', 'Queue ', self.numInQ, '\n')

            if self.count == self.maxCount :     ##########run will stop here###########
                i = 0
                while i < self.totalServed :
                    self.totalservertime += self.serviceBackup[i]
                    i += 1

                util = self.totalservertime / self.simclock
                #########average queue length of each queue#######
                for j in range(self.numOfServer):
                    self.avgQlengthofEach.append(self.Qlength[j] / self.simclock)
                ######mean value#####
                avgQlength = 0
                for j in range(self.numOfServer):
                    avgQlength += self.avgQlengthofEach[j]
                avgQlength = avgQlength / self.numOfServer
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


def experiment4():
    maxCount = 10000
    lambd = 5.0 / 60
    mu = 8.0 / 60
    numofServers = [u for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for k in numofServers:
        sim = Simulator()
        states = States()
        sim.configure(Params(lambd, mu, k), states, maxCount)
        sim.run()
        sim.printResults()

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl/k)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(numofServers, avglength)
    plt.xlabel('Num of Servers (k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(numofServers, avgdelay)
    plt.xlabel('Num of Servers (k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(numofServers, util)
    plt.xlabel('Num of Servers (k)')
    plt.ylabel('Util')

    plt.show()


def main():

    experiment4()


if __name__ == "__main__":
    main()