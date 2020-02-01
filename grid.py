
import animation
import config
import colours
import sys
import random
import requests
import pygame

from network import Node


class Grid():

    def __init__(self,wh,surface = None):

        if surface:
            self.mainSurface = surface
            #print("Window Size: {}".format(self.mainSurface.get_size()))
        else:
            self.mainSurface = None
        self.w = wh[0]
        self.h = wh[1]
        self.intersects = []
        self.boxList = []
        self.boxesContainingNodes = []
        self.visual = False
        self.sortedBoxList = []
        self.getBoxCoords()
        self.createBoxes()
        self.sortBoxList()

    def getBoxCoords(self):
        if self.mainSurface:
            self.w_screen, self.h_screen = self.mainSurface.get_size()
        else:
            self.w_screen, self.h_screen = (1440, 900)
        self.box_len_w = self.w_screen/self.w
        self.box_len_h = self.h_screen/self.h
        #get top left coords for the boxes
        #print("Box Size: {0},{1}".format(self.box_len_w,self.box_len_h))
        self.xPositions = []
        self.yPositions = []

        postionCounterx = 0
        postionCountery = 0

        self.xPositions.append(postionCounterx)
        self.yPositions.append(postionCountery)

        for i in range(self.w-1):
            postionCounterx += self.box_len_w
            self.xPositions.append(postionCounterx)
        for j in range(self.h-1):
            postionCountery += self.box_len_h
            self.yPositions.append(postionCountery)

        self.intersects = [(x,y) for x in self.xPositions for y in self.yPositions]


    def createBoxes(self):
        for boxCounter in range(self.w*self.h):
            newBox = Box(self.intersects[boxCounter],(self.box_len_w,self.box_len_h),70,boxCounter)
            if self.mainSurface:
                newBox.surface = self.mainSurface
            self.boxList.append(newBox)
        for box in self.boxList:
            if box.nodes:
                self.boxesContainingNodes.append(box)
        for box in self.boxList:
            box.grid = self

    def switchVisual(self,displaySurface):
        self.visual = True
        self.mainSurface = displaySurface
        for box in self.boxList:
            box.surface = self.mainSurface

    def show(self):
        for box in self.boxList:
            box.addBoxToMainSurf()

    def showBox(self,pos):

        for box in self.boxList:
            if box.inBox(pos[0],pos[1]):
                box.showThisBox()

    def addIdleToBox(self,pod):
        '''
        loops through boxes to see if coordinate matches
        '''
        for box in self.boxesContainingNodes:
            if box.inBox(pod.x,pod.y):
                box.currentPodsContained.append(pod)
                pod.idleBox = box
                return

    def findPodsBox(self,pod):
        for box in self.boxesContainingNodes:
            if box.inBox(pod.x,pod.y):
                return box

    def sortBoxList(self):
        self.sortedBoxList = []
        subList = []
        for k in self.yPositions:
            subList = [box for box in self.boxList if box.topLeftCoords[1] == k]
            subList.sort(key = self.sortCoords)
            self.sortedBoxList += subList

    def sortCoords(self,box):
        return(box.topLeftCoords[0])

    def clearGridData(self):
        for box in self.boxList:
            box.clearData()



class Box():

    def __init__(self,topLeftCoords,size,alpha,Id,surface = None):
        self.nodes = []
        self.pods = []
        self.coords = None #((TL),(TR),(BL),(BR)) #Will be a tuple of 4 containing xy tuples

        self.topLeftCoords = topLeftCoords
        self.size = size
        self.surface = surface
        self.Id = Id
        self.alpha = alpha

        self.colour = (200,0,0)
        self.alphaRange = [10,110,140,160,170,180,190,200,210,220]
        self.clickedAlpha = 120
        self.clickedColour = (111,0,255) #(111,0,255)
        self.flashColour = (200,10,10)
        self.flashFreq = [ 100,75,50,25,13,6,3]
        self.flashAlpha = 50
        self.flashed = False
        self.flashedCounter = 0
        self.surplus = False
        self.surplusColour = (255,87,3)
        self.surplusAlpha = [20,70,100,120,140,150,160,180]
        self.label = False


        self.showBox = False #To show individual box
        self.getContainedNodes()
        self.targetPodsContained =  0
        self.currentPodsContained = []

        self.grid= None
        self.numRequests = 0
        self.numMissingPods = 0
        self.numExtraPods = 0
        self.pendingRequests = []
        self.liveRequests = []

    def inBox(self,xPos,yPos):
        TL = self.coords[0]
        TR = self.coords[1]
        BL = self.coords[2]
        BR = self.coords[3]
        #If it falls into the x and y region of the box
        #Remeber that pygame coordinate frame is inverted
        if xPos >= TL[0] and xPos < TR[0] and yPos <= BL[1] and yPos > TL[1]:
            return True
        else:
            return False

    def showThisBox(self):
        if not self.showBox:
            self.showBox = True
        else:
            self.showBox = False


    def getContainedNodes(self):
        '''
        Take the coordinates of the box corners, then go through the nodes file, passing the node coordinates to inBox function which checks if the node is in the box, thus appending it to the nodes attribute. If there are no contained nodes in the box, the alpha level is set to transparent grey
        '''
        self.getCornerCoords()
        with open('./resources/MapData/nodes.dat' ,'r') as nodeFile:
            line = True
            while line:
                line = nodeFile.readline()
                if len(line.strip())<1:
                    break
                details = line.strip().split(',')
                node = Node(float(details[0]),float(details[1]),details[2])
                #print(node))
                if self.inBox(node.x,node.y):
                    self.nodes.append(node)

        if not self.nodes:
            self.alpha = random.randint(20,70)
            self.colour = (99,88,88)


    def getCornerCoords(self):
        TL = self.topLeftCoords
        TR = (TL[0]+ self.size[0],TL[1])
        BL = (TL[0], TL[1] + self.size[1])
        BR = (TL[0]+ self.size[0],TL[1] + self.size[1])
        self.coords = (TL,TR,BL,BR)


    def addBoxToMainSurf(self):
        s = pygame.Surface(self.size)  # the size of rect

        if self.showBox:
            s.set_alpha(self.clickedAlpha)        # alpha level (0-255)
            s.fill(self.clickedColour)
        elif self.flashed:
            s.set_alpha(self.alpha-10)
            s.fill(self.flashColour)
        elif self.surplus:
            s.set_alpha(self.surplusAlpha[self.numExtraPods])
            s.fill(self.surplusColour)
        else:
            s.set_alpha(self.alpha)
            s.fill(self.colour)

        if self.label:
            font = pygame.font.SysFont(config.fontPodText, 30)
            text = font.render(str(self.Id), True, (0,0,0))

            if self.nodes:
                text2 = font.render(str(self.targetPodsContained), True, (0,0,0))
                text3 = font.render(str(len(self.currentPodsContained)), True, (0,0,0))
                s.blit(text2, (self.size[0]-14,self.size[1]-20 ))
                s.blit(text3, (0,self.size[1]-20 ))
                s.blit(text, (0, 0))

        #pygame.display.flip()
        self.surface.blit(s,self.topLeftCoords)

    def checkTargetContainedPods(self,podFleet,simulationTime,network):
        '''
        Function for boxes to check that they have the target number of pods. If they have more they add it to the surplus array.If they have less they make a pod request
        '''
        if len(self.currentPodsContained) < self.targetPodsContained:
            self.makeIdleRequest(podFleet,simulationTime,network)

        if len(self.currentPodsContained) > self.targetPodsContained:
            self.notifyPodFleetOfSurplus(podFleet)

        else:
            self.surplus = False

    def makeIdleRequest(self,podFleet,simulationTime,network):

        self.numMissingPods = self.targetPodsContained - len(self.currentPodsContained)

        if (len(self.pendingRequests)+len(self.liveRequests)) < self.numMissingPods:#Caps the number of equests that can be submitted

            newRequest = requests.BoxRequest(self,random.choice(self.nodes),simulationTime,network)
            self.pendingRequests.append(newRequest)
            podFleet.queuedBoxRequests.append(newRequest)

        self.flashedCounter +=1
        try:
            self.flashed = not(self.flashedCounter % self.flashFreq[self.numMissingPods])
        except IndexError:
            self.flashed = 1

    def notifyPodFleetOfSurplus(self,podFleet):
        self.numExtraPods = len(self.currentPodsContained) - self.targetPodsContained
        if self.pendingRequests:
            for i in range(self.numExtraPods):
                try:
                    delRequest = self.pendingRequests.pop()#Only remove from requests still pending, not those in progress
                except IndexError:
                    continue
                if delRequest in podFleet.queuedBoxRequests:
                    podFleet.queuedBoxRequests.remove(delRequest)#ensure that it is also removed form the main request handler
        surplusPod  = random.choice(self.currentPodsContained)
        surplusPod.surplusSourceBox = self
        podFleet.surplusBoxPods.append(surplusPod)


    def updateIdleCount(self,podFleet):
        for idlePod in podFleet.status1Pods:
            if self.inBox(idlePod.x,idlePod.y):
                self.currentPodsContained.append(idlePod)

    def findPodsBox(self,pod):
        return self.grid.findPodsBox(pod)

    def clearData(self):
        self.__init__(self.topLeftCoords,self.size,70 ,self.Id,surface = self.surface)











