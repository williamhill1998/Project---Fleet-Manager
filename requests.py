import os
import datetime

def clearSummaryFile():
    print("Clearing Request Summary file")
    try:
        os.unlink(r'./resources/RequestData/RequestSummary.dat')
    except OSError as e:
        #print ("Error: %s - %s." % (e.filename, e.strerror))
        pass

class Request:

    def __init__(self,Id):
        self.Id = Id
        self.date = None
        self.TSubmit = None
        self.TPickUp = None
        self.TDropOff = None
        self.serviceTime = None
        self.PodUsed = None
        self.startNode= None
        self.endNode = None
        self.requestSummaryPath = r'./resources/RequestData/RequestSummary.dat'



    def complete(self):
        submitDatetime = datetime.datetime.combine(self.TDropOff.date(), self.TSubmit)
        self.serviceTime = self.TDropOff - submitDatetime
        serviceTimeSeconds = self.serviceTime.total_seconds()
        walkTime = self.PodUsed.calcWalkTime() #seconds
        # print('Service time in seconds: {0:.0f} \t Walk time in seconds {1:.0f}\n'.format(serviceTimeSeconds,walkTime))
        if walkTime > 0.5*serviceTimeSeconds:
            return True
        else:
            return False

        # with open(self.requestSummaryPath,'a') as summary:
            # summary.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(self.Id,self.TSubmit,self.TPickUp,self.TDropOff,self.startNode,self.endNode,self.PodUsed,self.serviceTime))

class BoxRequest:

    def __init__(self,requestingBox,endNode,requestTime,pathNetwork):
        self.pathNetwork = pathNetwork
        self.requestingBox = requestingBox
        self.endNode = endNode
        self.requestTime = requestTime
        self.arriveTime = None
        self.podUsed = None
        self.endNodeCoords = None
        self.numMissingPods = self.requestingBox.numMissingPods
        self.getEndNodeCoords()

    def getEndNodeCoords(self):
        self.endNodeCoords = self.pathNetwork.getCoordinatesForNodeList(int(self.endNode.name))
        return self.endNodeCoords









