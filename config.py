# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:01:13 2017

@author: Roger Woodman and William Hill
"""
import colours
import datetime

"""
This contains the configuration file for the sleet setup.  There are better
ways of doing this, like using a data text file.  However, doing it like this
is much faster and allows direct access to the config parameters
"""

# Pod system settings
maxNumberOfPods = 30
podSize = 7
podFontSize = 14
podMaxSpeed = 1.5  # km/h (2)
animationStartSpeed = 500

# Route settings
commonDestinations = [1, 90]  # Node indices

randomPodSpeed = False
randomPodStartTime = False
numRequests = 200
requestSpacing = 10 #minutes
useWorkSchedule = True #WS
#localisedRequests = [1, 2] #WS
localisedRequests = None
viewRequestGraphs = False
weightedRequest = True
tournament = False


# 2230 metres = 1440 pixels
metresPerPixel = 1.548611111
walkingSpeed = 1.4  # m/s

# SWARM
swarmPairMaxDistance = 300
swarmMinBuddyingDistance = 400

# Drawing modes
drawBackground = True
drawPods = True
drawGraph = False
drawGrid = True
drawFramesToSkip = 1

currentDrawMode = 0  # Used to cycle through drawing modes
drawLabelDistanceToBuddy = False
drawLabelDistanceToDestination = False
drawLinesBetweenClosestPod = False
drawLineToDestination = False

simulationTimeStep = datetime.timedelta(seconds=100)  # 300 fastest

# Grid
gridDimensions = (20, 15)  # 20x15 ideal
visualGrid = True

# GA
GA = True
#GA = False

maxGenerationNum = 200
generationSize = 100
mutationProb = 0.01#0.01
crossoverProb = 0.7

if GA:
  print("Running in none Visual Mode")
  drawBackground = not GA
  drawPods = not GA
  drawGrid = not GA
  visualGrid = not GA

# Appearance
screenWidth = 1661  # 1661
screenHeight = 1429
lineThickness = 1
fontPodText = "freesansbold.ttf"
# Note: the lower the resolution this image, the faster the simulation will run
cityImage = r'resources/images/map2.png'
# cityImage = r'resources/images/map2_reduced90.jpg')
# cityImage = r'resources/images/map2_reduced70.jpg')

podTextColour = colours.LIGHTPURPLE
podMainColour = colours.LIGHTSTEELBLUE3
podCoupledColour = colours.PALEVIOLETRED
podBuddyingNotAllowedColour = colours.AQUAMARINE1
podBorderColour = colours.BLACK

status1Colour = colours.LIGHTSTEELBLUE3  # LIGHTSTEELBLUE3
status2Colour = colours.AQUAMARINE1
status3Colour = colours.PALEVIOLETRED
status4Colour = colours.STEELBLUE

status1BorderColour = colours.BLACK
status2BorderColour = colours.BLACK
status3BorderColour = colours.BLACK
status4BorderColour = colours.BLACK


markerDestinationColour = colours.RED2
lineBuddyingAllowedColour = colours.AQUA
