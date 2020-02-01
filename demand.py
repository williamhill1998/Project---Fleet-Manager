
##import networkx?
##Need to import the graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import datetime
import network
import random
import config
import numpy
from requests import Request

class DemandGenerator(object):
    def __init__(self):
        self.datetime = datetime.datetime(2018,6,1,7) #start at 7am
        self.request = ''
        self.pathNetwork = network.PathNetwork(config.drawGraph)
        self.nodeList = self.pathNetwork.getNodeList()
        self.allRequests = []


    def createWorkDayRequestSchedule(self):
        #a(0)x^5 + a(1)x^4 + a(2)x^3 + a(3)x^2 + a(4)x + a(5)
        # print("Creating Workday demand...")
        trafficAvg = [1525.81666666667,2031.08333333333,1461.58333333333,1284.13333333333,1360.05000000000,1469.41666666667,1534.38333333333,1554.55000000000,1738.35000000000,2054.06666666667,2119.76666666667,1558.31666666667]
        hours = [7,8,9,10,11,12,13,14,15,16,17,18]
        P = numpy.polyfit(hours,trafficAvg,7)
        fractionOfHour = config.requestSpacing / 60
        x = numpy.arange(7,18,fractionOfHour)
        xCont = numpy.linspace(7,18,1000)
        datapoints = numpy.polyval(P,x)
        yfit = numpy.polyval(P,xCont)
        normalisedY = numpy.divide(datapoints,sum(datapoints))
        self.requestSchedule = numpy.multiply(config.numRequests , normalisedY)
        self.requestSchedule = [int(round(x)) for x in self.requestSchedule]
        if config.viewRequestGraphs:
            f, (ax1, ax2) = plt.subplots(2, 1 ,sharex = True)
            ax1.plot(xCont,yfit)
            ax1.plot(hours,trafficAvg)
            ax1.plot(x,datapoints,"|")
            ax2.plot(x,self.requestSchedule)
            plt.show()


    def createRequestObj(self,Id):
        self.nodeList = self.pathNetwork.getNodeList()
        newRequest = Request(Id)
        newRequest.date = self.datetime.date()
        newRequest.TSubmit = self.datetime.time()
        if config.localisedRequests:
            nodeLocalisedList = [self.pathNetwork.graphMain.getNodeByName(nodeName) for nodeName in config.localisedRequests]
            newRequest.startNode = random.choice(nodeLocalisedList)
        elif config.weightedRequest:
            nodes = self.nodeList
            if 1 == random.randint(1,4):
                newRequest.startNode = self.pathNetwork.graphMain.getNodeByName(1)
            elif 2 == random.randint(1,4):
                newRequest.startNode = self.pathNetwork.graphMain.getNodeByName(60)
            else:
                newRequest.startNode = random.choice(self.nodeList)
        else:
            newRequest.startNode = random.choice(self.nodeList)
        self.nodeList.remove(newRequest.startNode)
        newRequest.endNode = random.choice(self.nodeList)
        return newRequest


    def generateArray(self):
        self.allRequests = []
        if config.useWorkSchedule:
            self.createWorkDayRequestSchedule()
            for reqNum in self.requestSchedule:
                for i in range(1,reqNum):
                    newRequest = self.createRequestObj(i)
                    self.allRequests.append(newRequest)
                self.jumpTime(fixed = config.requestSpacing)

        else:
            for i in range(config.numRequests):
                newRequest = self.createRequestObj(i)
                self.allRequests.append(newRequest)
                self.jumpTime()
        # print([req.TSubmit for req in self.allRequests ])
        return self.allRequests

    def jumpTime(self, fixed = None):
        if fixed:
            minute_jump = fixed
        else:
            minute_jump = random.randrange(1,15)
        self.datetime = self.datetime + datetime.timedelta(minutes=minute_jump)

if __name__ == "__main__":
    demand = DemandGenerator()
    demand.generateArray()
































