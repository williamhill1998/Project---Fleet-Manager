# -*- coding: utf-8 -*-
"""
Created on Fri May 11 11:18:29 2018

@author: Roger Woodman
"""
import datetime
import random

class SystemStatistics:
    """
    This is a class is essentially a placeholder.
    It allows the generation of statistics that look about right.

    TODO: Generate actual statisitcs based on the pod fleet
    """
    def __init__(self, podFleet):
        """
        Initialise the statisitics variables and record the current time
        """
        self.podFleet = podFleet
        self.podJourneyCount = 0
        self.passengerCount = 0
        self.statistics = []
        self.updateCount = 0
        self.startTime = datetime.datetime.now()
        self.customString = []
        self.recSize = 100

    def averagePassengersPerPod(self):
        """
        Get the average number of passengers per pod
        TODO: Implement this properly
        """
        if self.podJourneyCount == 0 or self.passengerCount == 0:
            return 0
        return self.passengerCount / self.podJourneyCount

    def getStatsArray(self):
        """
        Get the current statisitics as a string array
        TODO: Implement this properly
        """
        if(self.updateCount > 10):
            self.statistics = []
            currentTime = datetime.datetime.now()
            #currentRunningTime = (currentTime - self.startTime).total_seconds()* 60
            #currentRunningTimeHours = divmod(currentRunningTime, 3600)[0]
            #currentRunningTimeMinutes = divmod(currentRunningTime, 60)[0]
            if self.customString:
                self.recSize = 80
                for item in self.customString:
                    self.statistics.append(item)
                    self.recSize +=20
            # self.statistics.append("Average speed: %s km/h" % (round(random.uniform(12,14), 1)))
            # self.statistics.append("" % (round(currentRunningTimeMinutes)))
            self.updateCount = 0
        self.updateCount +=1
        return self.statistics

    def addCustomString(self,string):
        #want the array to refresh after every loop
        self.customString.append(string)

    def refreshCustomString(self):
        self.customString = []

