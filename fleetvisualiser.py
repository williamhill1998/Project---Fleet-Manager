# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 12:55:12 2017

@author: Roger Woodman
"""


# import my modules

import network
import podhandler
import algorithm
import animation
import colours
import systemstatistics
import datetime
import requests
import grid
import demand
import sys
import config

if(config.drawBackground or config.drawPods):
    import matplotlib
    import pygame
import time
import math


class App:
    """
    Main fleet visualiser class.
    """
    def __init__(self,geneticGrid = None,chromosome = None):

        self.simulationRunning = True
        self.showStatistics = True
        self.currentLoop = 0
        self.size = self.weight, self.height = config.screenWidth, config.screenHeight
        self.animationSpeed = config.animationStartSpeed
        self.pathNetwork = network.PathNetwork(config.drawGraph)
        if chromosome:
            self.chromosome = chromosome
            self.podFleet = podhandler.PodFleet(self.pathNetwork,self.chromosome)
        else:
            self.podFleet = podhandler.PodFleet(self.pathNetwork)

        if(geneticGrid):
            self.grid = geneticGrid

        else:
            self.grid = None

        self.algorithm = algorithm.Algorithm(self.podFleet)
        self.statistics = systemstatistics.SystemStatistics(self.podFleet)
        self.simulationTimeStep = config.simulationTimeStep

        self.FPS = None

    def onInit(self):
        """
        Draws the visualisation to the screen, depending on the configuration file
        """

        self.requestArray = demand.DemandGenerator().generateArray()
        if(config.drawBackground or config.drawPods):
            pygame.init()
            self.displaySurface = pygame.display.set_mode((0,0), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            # Maximize the pygame window
            # hwnd = win32gui.GetForegroundWindow()
            # win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            self.assetDrawing = animation.AssetDrawing(self.displaySurface)

        if(config.drawBackground):
            if(not self.grid):
                self.assetDrawing.drawBackgroundImage(config.cityImage, 0, 0)
                self.grid = grid.Grid(config.gridDimensions,surface = self.displaySurface)
            elif(self.grid and config.visualGrid):
                self.grid.switchVisual(self.displaySurface)

        self.simulationRunning = True
        self.simulationTime = datetime.datetime(2018,6,1,6,30)
        self.lastRequestDate = self.simulationTime.date()
        self.lastRequestTime = self.simulationTime.time()

        self.currentRequestIdx = 0


        self.pause = False
        #self.podFleet.clearPodData()
        #requests.clearSummaryFile()


        # For each pod in the fleet
        for podIndex, pod in enumerate(self.podFleet.podArray):
            # pod.createPodFolder("Route")
            pod.setXY(pod.startCoords)
            # pod.writeToPodFolder('Route',pod.startCoords,self.currentLoop)
            if config.drawPods:
                self.assetDrawing.drawPod(pod.x, pod.y, podIndex)



    def onEvent(self, event):
        """
        Handle key press events
        """

        if event.type == pygame.QUIT:
            self.simulationRunning = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            self.grid.showBox(pos)

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                self.pause = not self.pause

            if event.key == pygame.K_ESCAPE:
                self.simulationRunning = False

            if event.key == pygame.K_0:
                config.drawFramesToSkip += 5
                print("Increasing Speed")
                # Set max speed
                if config.drawFramesToSkip > 300:
                    config.drawFramesToSkip = 300

            if event.key == pygame.K_9:
                config.drawFramesToSkip -= 5
                print("Decreasing Speed")
                # Set min speed
                if config.drawFramesToSkip < 1:
                    config.drawFramesToSkip = 1

            if event.key == pygame.K_o:

                if self.simulationTimeStep >datetime.timedelta(seconds= 10):
                    self.simulationTimeStep -= datetime.timedelta(seconds= 10)
                elif self.simulationTimeStep <= datetime.timedelta(seconds= 10) and self.simulationTimeStep > datetime.timedelta(seconds= 0):
                    self.simulationTimeStep -= datetime.timedelta(seconds= 1)
                else:
                    self.simulationTimeStep = datetime.timedelta(seconds= 0)
                print('Decreasing Simulation Step {}'.format(self.simulationTimeStep))

            if event.key == pygame.K_p:
                if self.simulationTimeStep >= datetime.timedelta(seconds= 10):
                    self.simulationTimeStep += datetime.timedelta(seconds= 10)
                elif self.simulationTimeStep < datetime.timedelta(seconds= 10):
                    self.simulationTimeStep += datetime.timedelta(seconds= 1)
                print('Increasing Simulation Step {}'.format(self.simulationTimeStep))


            if event.key == pygame.K_d:
                config.drawLabelDistanceToBuddy = False
                config.drawLabelDistanceToDestination = False
                config.drawLinesBetweenClosestPod = False
                config.drawLineToDestination = False

                config.currentDrawMode +=1

                if(config.currentDrawMode == 1):
                    config.drawLabelDistanceToBuddy = True
                elif(config.currentDrawMode == 2):
                    config.drawLabelDistanceToDestination = True
                elif(config.currentDrawMode == 3):
                    config.drawLinesBetweenClosestPod = True
                elif(config.currentDrawMode == 4):
                    config.drawLineToDestination = True
                else:
                    config.currentDrawMode = 0

            if event.key == pygame.K_s:
                self.showStatistics = not self.showStatistics

            if event.key == pygame.K_v:
                config.drawGrid =  not config.drawGrid
            if event.key == pygame.K_b:
                for box in self.grid.boxList:
                    box.label = not box.label


    def updateStatistics(self):
        if(self.showStatistics):
            self.assetDrawing.drawRectangle((10, 10, 200, self.statistics.recSize), colours.WHITE)
            self.statistics.addCustomString("Simulation Time: {}".format(self.simulationTime.time()))
            self.statistics.addCustomString("Simulation Time Step: {}".format(self.simulationTimeStep))
            self.statistics.addCustomString("Refresh Speed: {}".format(config.drawFramesToSkip))
            self.statistics.addCustomString("Journeys Completed: {0}/{1}".format(self.statistics.podJourneyCount,config.numRequests))
            self.statistics.addCustomString("Successful Journeys: {0}/{1}".format(self.podFleet.successfulJourneys,self.statistics.podJourneyCount))
            self.statistics.addCustomString("Pod Speed: {0}km/h".format(config.podMaxSpeed))

            if self.FPS:
                self.statistics.addCustomString("FPS: {0:.2f}".format(float(self.FPS)))
            for index, statistic in enumerate(self.statistics.getStatsArray()):
                self.assetDrawing.drawText(statistic, 20, (index + 1) * 30, 20)
            self.statistics.refreshCustomString()

    def calculatePodPosition(self, pod):
        """
        Calculate the pod's new xy coordinates using the pod target and speed
        """
        steps_number = max(abs(pod.targetX - pod.sourceX), abs(pod.targetY - pod.sourceY)) #this finds the max number of steps it will take to get to the destinaiton
        if(steps_number==0): steps_number = 1
        stepx = (float(pod.targetX - pod.sourceX) / steps_number) * pod.speed#this scales the step size based on how many it will take to get to the destination times the speed of the pod- essentially setting a stepsize
        stepy = (float(pod.targetY - pod.sourceY) / steps_number) * pod.speed
        #if the y distance is smaller, this will make sure that the steps are larger
        if(pod.x != int(pod.targetX)):
            pod.setXY((pod.sourceX + stepx * pod.currentStep, pod.y))
        if(pod.y != int(pod.targetY)):
            pod.setXY((pod.x, pod.sourceY + stepy * pod.currentStep))
        # pod.writeToPodFolder('Route',(pod.sourceX + stepx * pod.currentStep,pod.sourceY + stepy * pod.currentStep),self.currentLoop)
        # Increment the current step
        self.currentLoop +=1
        pod.currentStep +=1
        #DEBUG
        if pod.status ==1:
            print("Calculating pod {0} position: ({1},{2}) ".format(pod.podId,pod.sourceX + stepx * pod.currentStep,pod.sourceY + stepy * pod.currentStep))

    def calculatePodPostitionTimeBased(self,pod):
        '''
        To base pod movement on the simulation time, it needs to be a function of elapsed time.

        calculateElapsedTime
        distanceToMove = pod.speed * elapsedTime
        betweenNodes = n1 , n2
        getNodeCoords
        calculate Distance between nodes
        work out proportion of (distanceToMove + cumulativeDistanceMoved between nodes.) / DistanceBetweenNodes
        multiply by n2x-n1x, n2y-n1y
        add these value to start node
        gives next coords, setXY

        if proportion >1, setXY to n2Coords
        '''
        elapsedTime = (self.simulationTime - self.previousSimulationTime).total_seconds()

        speedInMs = pod.speed/3.6

        distanceToMove = (speedInMs/config.metresPerPixel) *elapsedTime

        distanceBetweenNodes  = math.hypot(abs(pod.targetX - pod.sourceX), abs(pod.targetY - pod.sourceY))

        pod.cumulativeDistanceMoved += distanceToMove

        proportionMoved = pod.cumulativeDistanceMoved/distanceBetweenNodes



        self.currentLoop +=1
        if proportionMoved >= 1 :
            pod.jumpRemaining = pod.cumulativeDistanceMoved - distanceBetweenNodes
            pod.cumulativeDistanceMoved = 0
            pod.setXY((int(pod.targetX), int(pod.targetY)))
            pod.currentStep +=1


        else:
            distanceToMoveX = proportionMoved*(pod.targetX - pod.sourceX)
            distanceToMoveY = proportionMoved*(pod.targetY - pod.sourceY)
            pod.setXY((pod.sourceX + distanceToMoveX,pod.sourceY + distanceToMoveY))



    def checkNewRequests(self):
        """
        Looks at the Request file. If there is a timestamp that is before the current simulation time, the request is passed to a live_request file which is then processed through the Pod Handler Class.
        """
        with open(r'./resources/RequestData/requests.dat','r') as requestList:
                self.podFleet.newRequests = []
                requestLine = True

                while requestLine:
                    requestLine = requestList.readline()
                    if len(requestLine)<2:
                        print("No more requests. Simulation Completed in {:.2f}seconds".format(time.time() - self.startTime ))

                        return False
                    details = requestLine.strip(' ').split(',')
                    if len(details)< 2:
                        break
                    datetime_request_date = datetime.datetime.strptime( details[0].strip(' ') , '%Y-%m-%d')
                    datetime_request_time = datetime.datetime.strptime( details[1].strip(' ') ,'%H:%M:%S')
                    #want request to go through when the simulation time is grater than or equal to the request time
                    #also want search to only go from the time of the last request checked
                    if datetime_request_date.date() <= self.simulationTime.date() and datetime_request_time.time()<= self.simulationTime.time():
                        #condition cutting of lower end of request list
                        if datetime_request_date.date() >= self.lastRequestDate  and datetime_request_time.time() > self.lastRequestTime:
                        #condition cutting off upper end of request list

                            self.podFleet.newRequests.append(requestLine)
                            self.lastRequestDate =  datetime_request_date.date()
                            self.lastRequestTime = datetime_request_time.time()

                        else:
                            continue
                    else:
                        break
                    #dont want to waste time comparing requests that we know arent in time as they are sorted...
                    #if request fails writing to live due to time, stop searching
                if len(self.podFleet.newRequests) > 0:
                    self.podFleet.process_requests(r'./resources/RequestData/live_requests.dat')
                return True

    def checkNewRequests_GA(self):
        if self.currentRequestIdx <= len(self.requestArray)-1:
            #DEBUG
            #print("{1} out of {0} requests have been processed".format(len(self.requestArray),self.currentRequestIdx))
            requestDate = self.requestArray[self.currentRequestIdx].date
            requestTime = self.requestArray[self.currentRequestIdx].TSubmit
            if requestDate == self.simulationTime.date() and requestTime <= self.simulationTime.time():
                self.podFleet.processObjRequest(self.requestArray[self.currentRequestIdx])
                self.currentRequestIdx+=1
            return True
        else:
            return False


    def updatePodJourneys(self):
        """
        Will first check if the pod is between nodes, if so it will incriment the position. If it is on a node it will check if it is the destination or an intermediate node. If it is a destination then it will check if the node is on route to a passenger or if they have just delivered them. This will change the status of the pod.
        """
        # For each pod in the fleet

        for pod in self.podFleet.podArray:
            # Run the algorithm for each pod
            #self.algorithm.runAlgorithm(pod)
            if pod.status !=1:
            # Work out the pod's new coordinates

                # self.calculatePodPosition(pod)
                self.calculatePodPostitionTimeBased(pod)
            else:
            #Idle pods should remain at the same node until they get assigned a route
                pod.setXY(self.pathNetwork.getCoordinatesForNodeList(int(pod.currentNode.name)))
                #pod.writeToPodFolder('Route',self.pathNetwork.getCoordinatesForNodeList(pod.currentNode),self.currentLoop)

            if(pod.x == int(pod.targetX) and pod.y == int(pod.targetY) and pod.status != 1):
                # Change the Pod source x, y to the target x, y and reset the current step
                pod.cumulativeDistanceMoved = pod.jumpRemaining
                pod.setSource((pod.targetX, pod.targetY))

                if pod.podNodeRoute:
                    pod.currentStep = 1

                    if(pod.currentNodeIndex < len(pod.podNodeRoute)-1):
                        # Pod has reached an intermediate node (but not the target node)
                        # Change the target to the next node on the route
                        pod.currentNodeIndex +=1
                        pod.setTarget(pod.podCoordsRoute[pod.currentNodeIndex])

                       # print("Pod {0}, Pod Target set to {1} ".format(pod.podId,pod.podCoordsRoute[pod.currentNodeIndex]))

                    elif(pod.currentNodeIndex == len(pod.podCoordsRoute)-1): #final node in route
                        # Pod has reached destination. Create a new pod route, using the current desitnation node as the start node

                        if pod.status == 2:#pod going to start node
                            pod.setPodRoute(pod.route)
                            pod.setStatus(3)
                            pod.currentRequest.TPickUp = self.simulationTime
                        elif pod.status== 3:#pod got to destination
                            self.statistics.podJourneyCount +=1
                            pod.currentRequest.TDropOff = self.simulationTime
                            successBool = pod.currentRequest.complete()
                            if successBool:
                                self.podFleet.successfulJourneys +=1
                            else:
                                self.podFleet.unsuccessfulJourneys +=1
                            self.grid.addIdleToBox(pod)
                            pod.setStatus(1)
                            #print("Pod {} has reached it's destination".format(pod.podId))
                            # pod.setXY(self.pathNetwork.getCoordinatesForNodeList(pod.currentNode))
                            # pod.writeToPodFolder('Route',self.pathNetwork.getCoordinatesForNodeList(pod.currentNode),self.currentLoop)
                            #pod.writeToPodFolder('Route', (pod.x,pod.y), self.currentLoop)

                        #pod.setPodRoute(self.podFleet.createWeightedRoute(startNode = pod.getDestinationNode()))
                        elif pod.status == 4:
                            self.grid.addIdleToBox(pod)
                            pod.setStatus(1)
                            #pod.writeToPodFolder('Route', (pod.x,pod.y), self.currentLoop)
                            pod.currentRequest.arriveTime = self.simulationTime
                            pod.currentRequest.requestingBox.flashed = False


                        # Inititalise the pod source and target
                        if pod.status != 1:
                            pod.initialisePodSourceAndTarget()
                            pod.currentNodeIndex = 1



        self.podFleet.refreshPodStatusLists()
        self.podFleet.redistributeIdle(self.simulationTime,self.grid,self)


    def drawFrame(self):
        # If not worried about drawing the visualisation then can turn this off to make the code run much faster
        if(config.drawBackground and not self.currentLoop % config.drawFramesToSkip):
                 #Draw the entire background# This is very slow
                self.assetDrawing.drawBackgroundImage(config.cityImage, 0, 0)

        if (config.drawGrid and config.visualGrid and not self.currentLoop % config.drawFramesToSkip):
            self.grid.show()


        if(config.drawPods and not self.currentLoop % config.drawFramesToSkip):
            # For each pod in the fleet

            for podIndex, pod in enumerate(self.podFleet.podArray):
                if(config.drawLinesBetweenClosestPod):
                    closestPod = self.podFleet.findClosestPod(pod)
                    if(closestPod is not None):
                        self.assetDrawing.drawLine((pod.x, pod.y), (closestPod.x, closestPod.y), colours.BLUE, config.lineThickness)

                if(config.drawLabelDistanceToDestination):
                    distance = pod.calculateRouteDistanceRemaining()
                    self.assetDrawing.drawTextbox((pod.x-16, pod.y-20, 30, 10), colours.WHITE, colours.WHITE)
                    self.assetDrawing.drawText(str(int(round(distance,0))), pod.x-14, pod.y-20, 16, colours.BLACK)

                if(config.drawLineToDestination):
                    if(pod.buddyingAllowed):
                        self.assetDrawing.drawLine((pod.x, pod.y), pod.getDestinationCoords(), config.lineBuddyingAllowedColour, config.lineThickness)
                    elif(pod.podNodeRoute):
                        self.assetDrawing.drawLine((pod.x, pod.y), pod.getDestinationCoords(), colours.BLUE3, config.lineThickness)
                        self.assetDrawing.drawCircle(pod.coordsToInt(pod.getDestinationCoords()), config.markerDestinationColour, 5)

                if(not pod.buddyingAllowed):

                    self.assetDrawing.drawPod(pod.x, pod.y, podIndex, status = pod.status, buddyingAllowed = False)
                else:
                    # Draw a line betweeAQUAMARINE1n pods travelling to the same destination
                    closestPod, distance, isQueryPodCloserToDestination = self.podFleet.FindTheClosestPodOnTheSameRoute(pod)

                    if(closestPod is not None and isQueryPodCloserToDestination and distance < config.swarmPairMaxDistance):
                        #print("Pods {0} , {1} have coupled".format(pod.podId, closestPod.podId))
                        # Set that each pod is now coupled to each other
                        pod.podCoupledId = closestPod.podId
                        closestPod.podCoupledId = pod.podId

                        if(config.drawLabelDistanceToBuddy):
                            self.assetDrawing.drawLine((pod.x, pod.y), (closestPod.x, closestPod.y), colours.BLUE, config.lineThickness)
                            self.assetDrawing.drawTextbox((pod.x-22, pod.y-20, 30, 10), colours.WHITE, colours.WHITE)
                            self.assetDrawing.drawText(str(int(round(distance,0))), pod.x-20, pod.y-20, 16, colours.BLACK)

                        self.assetDrawing.drawPod(pod.x, pod.y, podIndex, coupled=True)
                    else:
                        self.assetDrawing.drawPod(pod.x, pod.y, podIndex)


            self.updateStatistics()
            # Draw the whole canvas to the screen.  Stops double buffering
            pygame.display.flip()


    def onLoop(self):
        """
        Main execution loop.
        """

        if(not self.pause):
            self.previousSimulationTime = self.simulationTime
            self.simulationTime = self.simulationTime + self.simulationTimeStep

            newRequestsExist = self.checkNewRequests_GA()
            if newRequestsExist or (len(self.podFleet.status3Pods)>0):
             #if there are new request or if there are still pords with passengers inside
                self.updatePodJourneys()
                self.drawFrame()

            else:
                self.simulationRunning = False
                endTime = time.time()- self.startTime
                # print("Finished in {:.2f}s".format(endTime))
                # print("Request Time: {0:.2f}ms;\tPod Position Update Time: {1:.2f}ms;\tVisualisationTime: {2:.2f}ms;\tTotal Time in Loop = {3:.2f}ms;\tRaw Time between Pygame Ticks: {4}ms   {5:.0f}".format(timeForRequest,timeForPodPostionUpdate,timeForVisualisation,timeTotal,self.clock.get_rawtime(),time.time()-self.startTime))


    def onCleanup(self):
        if(config.drawBackground or config.drawPods):
            matplotlib.pyplot.close('all')
            pygame.display.quit()
            pygame.quit()
            # Need to exit to prevent pygame continuing to run and preventing system exit
        #sys.exit(0)

    def onExecute(self):
        """
        This is the main while loop.  It calls the simulation onLoop function, which
        proccesses the movements of the pod fleet.
        Sets the speed of the simulation.
        """
        self.startTime = time.time()
        if(config.drawBackground or config.drawPods):
            self.clock = pygame.time.Clock()
        if self.onInit() == False:
            self.simulationRunning = False

        while(self.simulationRunning):
            # print("498:Simulation Running")
            if(config.drawBackground or config.drawPods):
                # Process user events
                for event in pygame.event.get():
                    self.onEvent(event)

            # Process the next itteration of the simulator
            self.onLoop()

            #print("Loop Time: {}, Loop capped time {}".format(clock.get_rawtime(),clock.get_rawtime()-clock.get_time()))

            # Pause for the next frame
            if(config.drawBackground or config.drawPods):
                self.FPS = self.clock.get_fps()
                if(self.animationSpeed < 300):
                    self.clock.tick(self.animationSpeed)



        # When the program exits, clean up all open objects
        self.onCleanup()
        # print(self.podFleet.successfulJourneys, self.podFleet.unsuccessfulJourneys)
        fitness = (self.podFleet.successfulJourneys / (self.podFleet.successfulJourneys + self.podFleet.unsuccessfulJourneys))*100
        return fitness



if __name__ == "__main__" :
    theApp = App()
    theApp.onExecute()
