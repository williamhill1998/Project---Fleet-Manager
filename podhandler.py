
from requests import Request
from pod import Pod
import sys
import random
import config
import math
import datetime
import os
import shutil


class PodFleet:
    """
    Handles multiple pod instances by assigning routes and comparing pod positions
    """
    def __init__(self, pathNetwork,chromosome = None):

        self.maxNumberOfPods = config.maxNumberOfPods
        self.podArray = []
        self.pathNetwork = pathNetwork #Graph object
        self.newRequests = []
        self.requestsList = []
        self.currentRequests = []
        self.waitingRequests = []
        self.requestNum = 1
        self.surplusBoxPods= []
        self.queuedBoxRequests = []
        self.boxRequestsInProgress = []
        self.status1Pods = []
        self.status2Pods = []
        self.status3Pods = []
        self.status4Pods = []

        self.successfulJourneys = 0
        self.unsuccessfulJourneys = 0

        if chromosome:
            self.chromosome = chromosome
            self.assignFleet()
        else:
            # Populate the podArray with pods (each with a new route)
            self.createPodFleet()

    def assignFleet(self):
        for podIndex in range(0, self.maxNumberOfPods):
            # Create new Pod

            self.podArray.append(Pod(podIndex, self.pathNetwork,allocatedStartBox = self.chromosome.genes[podIndex]))

            # Select a random speed for each pod
            if(config.randomPodSpeed):
                self.podArray[len(self.podArray)-1].speed = (random.randrange(7, 10) * 0.1)

    def createPodFleet(self):
        """
        Create a number of new pods and assign a new route.
        This is currently randomly assigned
        """
        for podIndex in range(0, self.maxNumberOfPods):
            # Create new Pod
            self.podArray.append(Pod(podIndex, self.pathNetwork))

            # Select a random speed for each pod
            if(config.randomPodSpeed):
                self.podArray[len(self.podArray)-1].speed = (random.randrange(7, 10) * 0.1)


    def createRandomRoute(self, startNode = None, destinationNode = None):
        """
        Create a completely random route
        """
        nodeList = self.pathNetwork.getNodeList()
        if(startNode is None):
            startNode = random.choice(nodeList)

        if(destinationNode is None):
            # The start node and destination node can not be the same
            nodeList.remove(startNode)
            destinationNode = random.choice(nodeList)

        # Return pod route
        return self.pathNetwork.getShortestPath(startNode, destinationNode)


    def createWeightedRoute(self, startNode = None, destinationNode = None):
        """
        Create a random route, but add a weighting for a list of popular destinations (as defined by the config file)
        """
        # 50% of the time create completely random route, 50% select common destinations
        if(random.randrange(0, 2) == 1 or len(config.commonDestinations) <= 1):
            return self.createRandomRoute(startNode, destinationNode)
        else:
            commonDestinations = config.commonDestinations.copy()

            if(startNode is None):
                startNode = random.choice(commonDestinations)

            if(destinationNode is None):
                # The start node and destination node can not be the same
                if(startNode in commonDestinations):
                    commonDestinations.remove(startNode)
                destinationNode = random.choice(commonDestinations)

            # Return pod route
            return self.pathNetwork.getShortestPath(startNode, destinationNode)

    def findClosestPod(self, queryPod):
        """
        This gets the X,y distance and not the distance that the pods must travel on its route
        """
        closestDistance = sys.maxsize
        closestPod = None

        for pod in self.podArray:

            if(pod.podId != queryPod.podId):

                distance = math.hypot(abs(pod.x - queryPod.x), abs(pod.y - queryPod.y))

                # Check if there is a closer pod than any already identified
                if(distance < closestDistance):
                    closestDistance = distance
                    closestPod = pod

        return closestPod

    def FindTheClosestPodOnTheSameRoute(self, queryPod):
        """
        Search the route and find the pod the shares the same route and is the closest to the queryPod
        """
        closestPod = None
        isQueryPodCloserToDestination = False
        distance = sys.maxsize
        podsOnTheSameRoute = []

        # Get all the pods that are travelling to the same destination in the same direction
        for pod in self.podArray:
            if(pod.podId != queryPod.podId):

                matchingNodeList = self.CheckHowMuchPodRoutesMatch(queryPod, pod)

                # Pod node list must be > 1 and all nodes in the pod route must be the same as the emaining nodes in the query pod list
                if(len(matchingNodeList) > 1 and len(matchingNodeList) >= len(queryPod.getRemainingRouteNodes())):
                    # If the matching list > 1, then the destinations must be the same
                    # and the node previous to the destination.  This means travelling in the same direction
                    podsOnTheSameRoute.append(pod)

        # From the list of pods travelling to the same destination, need to find
        # which pod is the closest
        queryPodRemaingRouteDistance = queryPod.calculateRouteDistanceRemaining()

        for pod in podsOnTheSameRoute:
            podRemaingRouteDistance = pod.calculateRouteDistanceRemaining()

            tempDistance = podRemaingRouteDistance - queryPodRemaingRouteDistance

            if(tempDistance > 0 and tempDistance < distance):
                distance = tempDistance
                closestPod = pod

                if(queryPodRemaingRouteDistance < podRemaingRouteDistance):
                    isQueryPodCloserToDestination = True

        return closestPod, distance, isQueryPodCloserToDestination

    def CheckHowMuchPodRoutesMatch(self, pod1, pod2):
        """
        Compare the node route of the two pods. Starting from the
        destination and work backwards, stop when nodes don't match
        """
        nodeIndex = 0
        matchingNodeList = []

        pod1Nodes = pod1.getRemainingRouteNodes()
        pod2Nodes = pod2.getRemainingRouteNodes()

        if(pod1Nodes is not None and pod2Nodes is not None):
            # makes a copy of the nodes in reverse
            pod1Nodes = pod1Nodes[::-1]
            pod2Nodes = pod2Nodes[::-1]

            for node in pod1Nodes:
                if(node == pod2Nodes[nodeIndex]):
                    matchingNodeList.append(node)
                else:
                    break

                # If there are more nodes in pod2 node list, then incremenr the index
                if(nodeIndex < len(pod2Nodes)-1):
                    nodeIndex += 1
                else:
                    break

        return matchingNodeList

    def calculatePodSpeed(self, pod):
        """
        Calculate the actual pod speed.
        This is done because setting the pod speed is not precise, but as long as we know the
        size of each edge on the route we can calculate it.
        """
        # Calculate excecution duration
        if(pod.startTime is not None):
            timeEnd = datetime.datetime.now()
            executionDuration = timeEnd - pod.startTime

            distanceInMetres = pod.distanceBetweenPointsInMetres((pod.sourceX, pod.sourceY), (pod.targetX, pod.targetY))
            if(distanceInMetres > 0 and executionDuration.total_seconds() > 0):
                metresPerSecond = distanceInMetres / executionDuration.total_seconds()
                kmPerHour = metresPerSecond * 3.6
                print(pod.currentNodeIndex, "distance: ", round(distanceInMetres,2), "metres, ", round(metresPerSecond, 2), "m/s", round(kmPerHour, 2), "km/h")


    def clearPodData(self):
        path = r"./resources/PodData"
        #print("Clearing Pod Data file")
        for file in os.listdir(path) :
            if not file.startswith('.'):
                try:
                    fullPath = os.path.join(path, file)
                    shutil.rmtree(fullPath)
                except OSError as e:
                    print ("Error: %s - %s." % (e.filename, e.strerror))


    def process_requests(self,in_file):
        #The assignment will be based on the proximity of the pod to the request point
        requestsList= []
        if len(self.waitingRequests)> 0 :
            for request in self.waitingRequests:
                closestPod = self.findClosestRequestPod(request.startNode)
                if closestPod:
                    self.assignPod(closestPod,request)
                    self.waitingRequests.remove(request)
                    #print("Waiting request {0} to {1} is being completed\nThere are {2} requests waiting".format(request.startNode,requestDict["endNode"],len(self.waitingRequests)))

        for req in self.newRequests:
            details = req.strip(' ').split(',')
            if len(details) < 4:
                break
            if len(details) == 4:
                requestDict = {
                            "date" : details[0],
                            "time" : details[1],
                            "startNode" : int(details[2].strip(" ")),
                            "endNode" : int(details[3].strip(" "))
                            }

                dateTimeStr = details[0] + details[1]

                newRequest = Request(self.requestNum)
                newRequest.TSubmit = self.strToDateTime(dateTimeStr)
                newRequest.startNode = int(requestDict['startNode'])
                newRequest.endNode = int(requestDict['endNode'])
                requestsList.append(newRequest)


                closestPod = self.findClosestRequestPod(requestDict["startNode"])

                self.requestNum +=1
                if closestPod:
                    newRequest.PodUsed = closestPod
                    self.assignPod(closestPod,newRequest)


                else:
                    print("No pods availible for request {0} to {1}".format(requestDict["startNode"],requestDict["endNode"]))
                    self.waitingRequests.append(newRequest)

    def processObjRequest(self,requestObj):
        if len(self.waitingRequests)> 0 :
            for request in self.waitingRequests:
                closestPod = self.findClosestRequestPod(request.startNode)
                if closestPod:
                    self.assignPod(closestPod,request)
                    self.waitingRequests.remove(request)
                # dateTimeStr = str(requestDict.date) + str(requestDict.time)

        self.requestsList.append(requestObj)
        closestPod = self.findClosestRequestPod(requestObj.startNode)
        self.requestNum +=1

        if closestPod:
            requestObj.PodUsed = closestPod
            self.assignPod(closestPod,requestObj)
        else:
            self.waitingRequests.append(requestObj)


    def assignPod(self,pod,request,BoxRequest = False,Visualiser = False):
        #PodHandler function to assign a pod with a route, still need to get the pod to that route in the shortest distance, should this be dont through the manager or the pod? Through pod handler in case it gets decided through specific algorithms.
        try:
            pod.idleBox.currentPodsContained.remove(pod)
            pod.idleBox = None
        except AttributeError:
            if Visualiser:
                Visualiser.pause = True

        if not BoxRequest:
            pod.startNode = request.startNode
            pod.endNode = request.endNode
            routeToStart= self.pathNetwork.getShortestPath(int(pod.currentNode.name),int(pod.startNode.name))
            route = self.pathNetwork.getShortestPath(request.startNode.name,request.endNode.name)

            if len(routeToStart) < 2: #It is on the node for passenger pick up
                pod.setPodRoute(route)
                pod.setStatus(3)
            else:
                pod.setPodRoute(routeToStart)
                pod.setStatus(2)

            pod.currentRequest = request
            pod.route = route
            self.cancelBoxRequest(request.endNode)
        else:
            route = self.pathNetwork.getShortestPath(int(pod.currentNode.name),int(request.endNode.name))
            pod.setPodRoute(route)
            pod.currentRequest = request
            pod.route = route
            pod.setStatus(4)
            request.requestingBox.pendingRequests.remove(request)
            request.requestingBox.liveRequests.append(request)
            #print("Pod {0} relocating to Box {1}".format(pod.podId,request.requestingBox.Id))

        pod.initialisePodSourceAndTarget()

        #print("Pod {0} has been assinged a journey from {1} to {2}".format(pod.podId,pod.startNode,pod.endNode))


    def findClosestRequestPod(self,requestNode):
        #Checks for nearest idle pod to the request location
        closestDistance = sys.maxsize
        closestPod = None
        nodeCoords = self.pathNetwork.getCoordinatesForNodeList(int(requestNode.name))
        for pod in self.podArray:
            if pod.status == 1:
                distance = math.hypot(abs(pod.x - nodeCoords[0]), abs(pod.y - nodeCoords[1]))
                # Check if there is a closer pod than any already identified
                if(distance < closestDistance):
                    closestDistance = distance
                    closestPod = pod
        return closestPod

    def strToDateTime(self,timeStr):
        dateTimeType = datetime.datetime.strptime(timeStr , '%Y-%m-%d %H:%M:%S')
        return dateTimeType


    def checkNumQueuedBoxRequests(self,Box):
        allRequests = self.queuedBoxRequests + self.boxRequestsInProgress
        counter = 0
        for request in allRequests:
            if request.requestingBox.Id == Box.Id:
                counter +=1
        return counter

    def cancelBoxRequest(self,endNode):
        '''
        Cancels a box request if it sees that a passenger has requested one of it's nodes as a destination
        '''
        for request in self.queuedBoxRequests:
            xNode, yNode = request.getEndNodeCoords()
            if request.requestingBox.inBox(xNode, yNode):
                request.requestingBox.pendingRequests.remove(request)
                self.queuedBoxRequests.remove(request)

    def serviceBoxRequests(self,vis):
        closestRequest = None

        for surplusPod in self.surplusBoxPods:
            closestRequest = self.findClosestRequest(surplusPod)
            if closestRequest:
                if closestRequest.endNode == surplusPod.currentNode:
                    #A surplus pod should not be found in the same box that is requesting more pods...
                    # containedPodIds = [pod.podId for pod in closestRequest.requestingBox.currentPodsContained ]
                    # print("Failed due to request endNode and podCurrentNode being the same")

                    # boxPodIsIn = closestRequest.requestingBox.findPodsBox(surplusPod)
                    # boxContainsNodes = [node.name for node in closestRequest.requestingBox.nodes]

                    # raise Exception("Box {0} requested a surplus pod. The pod became surplus in Box {6}.\n'Surplus' Pod {3} has a current Node ({7})that is inside this box [{9}].\nAt the time of servicing the request it contained {1} pod(s) and has a target of {2}.\nBased on Coordinates the pod is in Box {8}\nContained Pods: {4}. Pod Status History:{5}. Current Status {10}\n ".format(closestRequest.requestingBox.Id,  len(closestRequest.requestingBox.currentPodsContained),  closestRequest.requestingBox.targetPodsContained,  surplusPod.podId,  containedPodIds,surplusPod.statusHistory,surplusPod.surplusSourceBox.Id,closestRequest.endNode.name,boxPodIsIn.Id,boxContainsNodes,surplusPod.status))

                    continue
                    '''
                    There are cases where the current Node of the surplus pod is the same as that of the request, if this is the case it should just skip it, couldnt find the source of the error!
                    '''
                else:
                    try:
                        self.queuedBoxRequests.remove(closestRequest)

                    except ValueError:
                        raise Exception("Tried to remove request from queuedBoxRequests, but could not find it. Request: {0}. Queued Box Requests: {1}".format(closestRequest,self.queuedBoxRequests))
                #Error-closestRequest is not in queuedBoxRequests-
                    self.surplusBoxPods.remove(surplusPod)
                    self.assignPod(surplusPod,closestRequest,BoxRequest = True, Visualiser= vis)
                    closestRequest.podUsed = surplusPod

                    self.boxRequestsInProgress.append(closestRequest)

    def findClosestRequest(self,surplusPod):

        closestDistance = sys.maxsize
        if self.queuedBoxRequests:
            for request in self.queuedBoxRequests:
                coords = request.endNodeCoords
                distance = math.hypot(abs(surplusPod.x - coords[0]), abs(surplusPod.y - coords[1]))
                    # Check if there is a closer pod than any already identified
                if(distance < closestDistance):
                    closestDistance = distance
                    closestRequest= request

            return closestRequest

        else:
            return None

    def redistributeIdle(self,time,grid,vis):
        # print(len(self.queuedBoxRequests))
        self.surplusBoxPods = []
        for box in grid.boxesContainingNodes:
            box.checkTargetContainedPods(self,time,self.pathNetwork)
        self.serviceBoxRequests(vis)

    def refreshPodStatusLists(self):
        self.status1Pods = [pod for pod in self.podArray if pod.status == 1]
        self.status2Pods = [pod for pod in self.podArray if pod.status == 2]
        self.status3Pods = [pod for pod in self.podArray if pod.status == 3]
        self.status4Pods = [pod for pod in self.podArray if pod.status == 4]











