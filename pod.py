import podhandler
import sys
import random
import config
import math
import datetime
import os
import shutil
import grid
import requests
from network import Node

class Pod:
    """
    Each pod is represented as a pod object.  This contains lots of properties and get/set functions
    """
    def __init__(self, podId, pathNetwork,nodeRoute = None,allocatedStartBox = None):
        self.statusHistory = []
        self.podId = podId

        self.x = 0
        self.y = 0

        self.sourceX = 0
        self.sourceY = 0
        self.targetX = 0
        self.targetY = 0


        self.startTime = None

        self.currentRequest = None

        self.idleBox = None

        # Pod must have knowledge of the available routes
        self.pathNetwork = pathNetwork

        if(nodeRoute):
            self.setPodRoute(nodeRoute)
        if allocatedStartBox:
            self.allocatedStartBox = allocatedStartBox

        self.route = None
        self.podCoordsRoute = None
        self.podNodeRoute = None

        self.currentNodeIndex = 1
        self.currentStep = 1
        if not allocatedStartBox:
            #This attribute only has a value when the pod is on a node
            self.currentNode =  random.choice(self.pathNetwork.getNodeList())##Returns with Node object list
        else:
            self.currentNode =  random.choice(self.allocatedStartBox.nodes)
            self.idleBox = self.allocatedStartBox

            self.allocatedStartBox.targetPodsContained += 1
            self.allocatedStartBox.currentPodsContained.append(self)
            try:
                self.allocatedStartBox.alpha= self.allocatedStartBox.alphaRange[self.allocatedStartBox.targetPodsContained]
            except IndexError:
                self.allocatedStartBox.alpha = self.allocatedStartBox.alphaRange[-1]

        self.startCoords = self.pathNetwork.getCoordinatesForNodeList(int(self.currentNode.name))

        # Allow pods to be stopped, slowed and paused
        self.speed = config.podMaxSpeed
        self.stopped = False
        self.waitTime = 0

        self.distanceCovered = 0
        self.podChargeState = 100
        self.buddyingAllowed = False
        self.podJourneysComplete = 0

        self.surplusSourceBox = None

        # Buddying state
        self.podCoupledId = None
        self.status = 1 #1- idle, 2- on way to start node 3- being used 4- Box request

        self.startNode = []
        self.endNode = []

        self.write_update_freq = 5 #write on every x loop
        self.lastData = {}

        self.cumulativeDistanceMoved = 0
        self.jumpRemaining = 0



    def initialisePodSourceAndTarget(self):
        try:
            self.setSource(self.podCoordsRoute[0])
            self.setTarget(self.podCoordsRoute[1])
        except IndexError:
            raise Exception("Failed to initialise. Coords Route: {0}.Length {1}".format(self.podCoordsRoute,len(self.podCoordsRoute)))

        self.setXY((self.sourceX, self.sourceY)) #this is the current pod position, on initialisation it is the sourcexy

        self.podCoupledId = None
        self.buddyingAllowed = False

        self.resetPodJourneyTimer()

    def resetPodJourneyTimer(self):
        # Set pod journey timer
        self.startTime = datetime.datetime.now()

    def setPodRoute(self, nodeRoute):
        self.podNodeRoute = nodeRoute
        self.podCoordsRoute = self.pathNetwork.getCoordinatesForNodeList(self.podNodeRoute)

    def saveCoordinate(self):
        pass

    def createPodFolder(self,fileName):
        pathFolder = r"./resources/PodData/Pod_{0}".format(self.podId)
        pathFile = pathFolder + "/{}.dat".format(fileName)

        folderExists = os.path.isfile(pathFolder)
        fileExists =os.path.isfile(pathFile)

        if not folderExists:
            os.mkdir(pathFolder)
        if not fileExists:
            with open(pathFile,'w') as dataFile:
                dataFile.write("")
        else:
            shutil.rmtree(pathFile)
            with open(pathFile,'w') as dataFile:
                dataFile.write("")

    def writeToPodFolder(self,fileName,data, currentLoop,writeRepeats = False):

        pathFolder = r"./resources/PodData/Pod_{0}".format(self.podId)
        pathFile = pathFolder + "/{0}.dat".format(fileName)
        fileExists =os.path.isfile(pathFile)
        if not fileName in self.lastData:
            self.lastData[fileName] = None
        if currentLoop%self.write_update_freq:
            if not fileExists:
                raise Exception("Writing to non existent data file: {}".format(pathFile))
            else:

                if writeRepeats:
                    with open(pathFile,'a') as dataFile:
                        dataFile.write("{}\t".format(data))

                else:
                    if self.lastData[fileName] != (int(data[0]),int(data[1])):
                        with open(pathFile,'a') as dataFile:
                            dataFile.write("{}\t".format(data))
                            self.lastData[fileName] = (int(data[0]),int(data[1]))

    def setXY(self, xy):
        self.x = int(xy[0])
        self.y = int(xy[1])

    def setSource(self, sourceXY):
        self.sourceX = int(sourceXY[0])
        self.sourceY = int(sourceXY[1])

    def setTarget(self, targetXY):
        self.targetX = int(targetXY[0])
        self.targetY = int(targetXY[1])


    def distanceBetweenPointsInMetres(self, sourceCoords, targetCoords):
        # Straight line distance between two coordinates
        distanceInPixels = math.hypot(abs(targetCoords[0] - sourceCoords[0]), abs(targetCoords[1] - sourceCoords[1]))

        # Convert distance to metres
        return distanceInPixels * config.metresPerPixel

    def getDestinationCoords(self):

        if self.podCoordsRoute:
            return self.podCoordsRoute[len(self.podCoordsRoute)-1]


    def coordsToInt(self, coords):
        return (int(round(coords[0])), int(round(coords[1])))

    def getDestinationNode(self):
        return self.podNodeRoute[len(self.podNodeRoute)-1]

    def getStartNode(self):
        return self.podNodeRoute[0]

    def getRemainingRouteNodes(self):
        return self.podNodeRoute[self.currentNodeIndex:]

    def calculatePodTotalRouteDistance(self):
        return self.calculateRouteDistance(self.podCoordsRoute)

    def calculateRouteDistanceRemaining(self):
        # Distance from the next node to the final node on the route
        if self.podNodeRoute:

            routeRemaining = self.calculateRouteDistance(self.podCoordsRoute[self.currentNodeIndex:])
            distanceToNextNode = self.distanceBetweenPointsInMetres((self.targetX, self.targetY), (self.x, self.y))
            routeRemaining += distanceToNextNode
        else:
            routeRemaining = 0
        return routeRemaining

    def calculateRouteDistance(self, routeCoords):
        """
        In metres calculate the distance between all of the coordinates for a given route
        """
        totalDistance = 0

        for nodeIndex in range(1, len(routeCoords)):

            # Source and target
            sourceCoords = routeCoords[nodeIndex - 1]
            targetCoords = routeCoords[nodeIndex]

            totalDistance += self.distanceBetweenPointsInMetres(sourceCoords, targetCoords)

        return totalDistance

    def setStatus(self, status):
        '''This method is to change the pods status, making the switching to idle more concise  and make it easier to have functions executing which a status change occurs'''
        self.statusHistory.append(self.status)
        if status ==1:
            self.status = 1
            self.podJourneysComplete += 1
            # self.currentNode = self.podNodeRoute[len(self.podCoordsRoute)-1]
            for node in self.idleBox.nodes:
                if int(node.name) == self.podNodeRoute[len(self.podCoordsRoute)-1]:
                    self.currentNode = node
            self.setXY((self.x,self.y))
            self.currentNodeIndex = 1
            self.podNodeRoute = None

            if type(self.currentRequest) is requests.BoxRequest:
                # print("Completed Box Request {0}".format(self.currentRequest))
                self.currentRequest.requestingBox.liveRequests.remove(self.currentRequest)


        elif status ==2:
            self.status = 2
        elif status == 3:
            self.status = 3
        elif status == 4:
            self.status = 4
        else:
            print("Pod {1} has invalid status ".format(self.podId))

    def calcWalkTime(self):
        distance = self.pathNetwork.graphMain.calculateTotalDistanceOfNodeList(self.podNodeRoute) #in pixels
        return distance * config.metresPerPixel *config.walkingSpeed #seconds




