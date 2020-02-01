import pygame
import animation
import config
import colours
import sys
import random

class App:

    def __init__(self):
        self.simulationRunning = True
        self.showStatistics = True
        self.currentLoop = 0
        self.size = self.weight, self.height = config.screenWidth, config.screenHeight
        self.animationSpeed = config.animationStartSpeed

    def onInit(self):
        pygame.init()
        self.displaySurface = pygame.display.set_mode((0,0), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        self.assetDrawing = animation.AssetDrawing(self.displaySurface)
        self.assetDrawing.drawBackgroundImage(config.cityImage, 0, 0)
        self.grid = Grid(self.displaySurface,10,10)

    def onEvent(self, event):
        if event.type == pygame.QUIT:
            self.simulationRunning = False

    def onLoop(self):

        self.assetDrawing.drawBackgroundImage(config.cityImage, 0, 0)
        self.grid.show()
        #rectangle = (1296.0, 810.0, 144.0,90.0)
        #pygame.draw.rect(self.displaySurface, colours.BLUE3 , pygame.Rect(rectangle),0)
        pygame.display.flip()


    def onExecute(self):
        clock = pygame.time.Clock()

        if self.onInit() == False:
            self.simulationRunning = False

        while(self.simulationRunning):

            if(config.drawBackground):
                # Process user events
                for event in pygame.event.get():
                    self.onEvent(event)

            # Process the next itteration of the simulator
            self.onLoop()

            # Pause for the next frame
            if(self.animationSpeed < 300):
                clock.tick(self.animationSpeed)


        # When the program exits, clean up all open objects
        self.onCleanup()

    def onCleanup(self):
        if(config.drawBackground or config.drawPods):
            pygame.display.quit()
            pygame.quit()
            # Need to exit to prevent pygame contiuning to run and prevening system exit
        sys.exit(0)


class Grid():

    def __init__(self,surface,w,h):
        self.surface = surface
        self.w = w
        self.h = h
        self.intersects = []
        self.boxList = []
        #print("Creating Grid")
        self.getBoxCoords()
        self.createBoxes()

    def getBoxCoords(self):
        self.w_screen, self.h_screen = self.surface.get_size()
        self.box_len_w = self.w_screen/self.w
        self.box_len_h = self.h_screen/self.h
        #get top left coords for the boxes
        print("Box Size: {0},{1}".format(self.box_len_w,self.box_len_h))
        xPositions = []
        yPositions = []

        postionCounterx = 0
        postionCountery = 0

        xPositions.append(postionCounterx)
        yPositions.append(postionCountery)

        for i in range(self.w-1):
            postionCounterx += self.box_len_w
            xPositions.append(postionCounterx)
        for j in range(self.h-1):
            postionCountery += self.box_len_h
            yPositions.append(postionCountery)

        self.intersects = [(x,y) for x in xPositions for y in yPositions]
        print(xPositions)
        print(yPositions)
        print(self.intersects)


    def createBoxes(self):
        for boxCounter in range(self.w*self.h):
            newBox = Box(self.surface,self.intersects[boxCounter],(self.box_len_w,self.box_len_h),random.randrange(100,200))
            self.boxList.append(newBox)

    def show(self):
        for box in self.boxList:
            box.showBox()



class Box():
    def __init__(self,surface,topLeftCoords,size,alpha):
        self.topLeftCoords = topLeftCoords
        self.size = size
        self.alpha = alpha
        self.nodes = []
        self.coords = None #((TL),(TR),(BL),(BR)) #Will be a tuple of 4 containing xy tuples
        self.colour = (200,180,255)
        self.surface = surface
        #print("Creating New Box")

    def getNodeContents(self):
        with open('./resources/MapData/nodes.dat' ,'r') as nodeFile:
            line = True
            while line:
                line = nodeFile.readline()
                details = line.split(',').strip('')
                node = {
                    'xPos' : details[0],
                    'yPos' : details[1],
                    'name' : details[2]
                }
                if node['xPos'] >= self.Coords[0][0] and node['xPos'] <= self.Coords[1][0]: #If it falls into the x region of the box
                    if node['yPos'] >= self.coords[2][1] and node['yPos'] <= self.Coords[0][1]:
                        self.nodes.append( int(node['name']))


    def getCornerCoords(self):
        pass

    def showBox(self):
        s = pygame.Surface(self.size)  # the size of your rect
        s.set_alpha(self.alpha)                # alpha level
        s.fill(self.colour)
        pygame.display.flip()
        self.surface.blit(s,self.topLeftCoords)





if __name__ == "__main__" :
    theApp = App()
    theApp.onExecute()

