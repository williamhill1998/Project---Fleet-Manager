    # -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:12:22 2017

@author: Roger Woodman and William Hill
"""
import pygame
import pygame.gfxdraw
import config
import colours

class AssetDrawing:
    """
    Draws the visualisation to the screen.
    Note: A lot of time has been spent optomising this, but there are limitations to
    python, which means it still runs slowly
    """
    def __init__(self, displaySurf):
        self.displaySurf = displaySurf
        pygame.font.init()

        self.podFontSize = config.podFontSize
        self.myfont = pygame.font.SysFont(config.fontPodText, self.podFontSize)
        self.backgroundImage = None
        self.podSize = config.podSize

    def drawPod(self, podX, podY, podNumber,status = 1, coupled = False, buddyingAllowed = True):
        if(status ==1):
            pygame.gfxdraw.filled_circle(self.displaySurf, podX, podY, self.podSize, config.status1Colour)
            pygame.gfxdraw.aacircle(self.displaySurf, podX, podY, self.podSize, config.status1BorderColour)
        elif(status == 2):
            pygame.gfxdraw.filled_circle(self.displaySurf, podX, podY, self.podSize, config.status2Colour)
            pygame.gfxdraw.aacircle(self.displaySurf, podX, podY, self.podSize, config.status2BorderColour)
        elif(status==3):
            pygame.gfxdraw.filled_circle(self.displaySurf, podX, podY, self.podSize, config.status3Colour)
            pygame.gfxdraw.aacircle(self.displaySurf, podX, podY, self.podSize, config.status3BorderColour)
        elif(status==4):
            pygame.gfxdraw.filled_circle(self.displaySurf, podX, podY, self.podSize, config.status4Colour)
            pygame.gfxdraw.aacircle(self.displaySurf, podX, podY, self.podSize, config.status4BorderColour)

        elif(coupled):
            pygame.gfxdraw.filled_circle(self.displaySurf, podX, podY, self.podSize, config.podCoupledColour)
            pygame.gfxdraw.aacircle(self.displaySurf, podX, podY, self.podSize, config.podBorderColour)
        else:
            pygame.gfxdraw.filled_circle(self.displaySurf, podX, podY, self.podSize, config.podMainColour)
            pygame.gfxdraw.aacircle(self.displaySurf, podX, podY, self.podSize, config.podBorderColour)

        if(self.podFontSize > 1):
            # Display number of passengers in pod on the pod marker
            textToDisplay = self.myfont.render(str(podNumber), True, config.podTextColour)
            textRectangle = textToDisplay.get_rect(center=(podX, podY+1))
            self.displaySurf.blit(textToDisplay, textRectangle)

    def drawMarker(self, markerRectangle, colour, text=None):
        pygame.draw.rect(self.displaySurf, colour, markerRectangle)

        if(text):
            lines = text.splitlines()
            yOffset = self.markerFontSize - 4 # Hacky

            for i, line in enumerate(lines):
                textToDisplay = self.myfont.render(line, True, colours.WHITE)
                textRectangle = textToDisplay.get_rect(center=(markerRectangle.x + int(markerRectangle.width/2),
                    yOffset + markerRectangle.y + (self.markerFontSize*i)))
                self.displaySurf.blit(textToDisplay, textRectangle)

    def drawText(self, text, x, y, fontSize, colour=colours.BLACK):
        font = pygame.font.SysFont(config.fontPodText, fontSize)
        self.displaySurf.blit(font.render(text, True, colour), (x, y))

    def drawBackgroundImage(self, imagePath, x, y, drawOnlyPodBackground = False):
        """
        Drawing the background is very time consuming.
        There are a few options here that allows only parts of the scene to be drawn on each refresh.
        """
        if(self.backgroundImage is None):
            self.backgroundImage = pygame.image.load(imagePath)
            self.backgroundImage = pygame.transform.scale(self.backgroundImage, (1440, 900))
            print("Loading", imagePath)
            self.displaySurf.blit(self.backgroundImage, (x, y))
        elif(drawOnlyPodBackground):
            # Create a rectangle slightly bigger than the pod
            dirtyRecWidth = (self.podSize * 2) + 2
            dirtyRecHeight = (self.podSize * 2) + 2
            rectX = x - (self.podSize + 1)
            rectY = y - (self.podSize + 1)

            # Calculate clean rect
            dirtyrect = self.backgroundImage.subsurface((rectX, rectY, dirtyRecWidth, dirtyRecHeight))

            # blit clean rect on top of "dirty" screen
            self.displaySurf.blit(dirtyrect, (rectX, rectY))
        else:
            self.displaySurf.blit(self.backgroundImage, (x, y))

    def drawTextbox(self, rectangle, colourBackground, colourBorder):
        pygame.draw.rect(self.displaySurf, colourBorder, pygame.Rect(rectangle), 2)
        pygame.draw.rect(self.displaySurf, colourBackground, pygame.Rect(rectangle), 0)

    def drawLine(self, point1, point2, colour, thickness):
        pygame.draw.line(self.displaySurf, colour, [point1[0], point1[1]], [point2[0], point2[1]], thickness)

    def drawCircle(self, coords, colour, size):
        halfSize = int(round(size/2))
        pygame.draw.circle(self.displaySurf, colour, (coords[0] + halfSize, coords[1] + halfSize), size, 0)

    def drawRectangle(self, markerRectangle, colour):
        pygame.draw.rect(self.displaySurf, colour, markerRectangle)

