# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 13:45:18 2018

@author: Roger Woodman
"""
import config

class Algorithm:
    """
    This is a placeholder class for when we want to add some "smarts" to the pods.
    """
    def __init__(self, podFleet):
        self.podFleet = podFleet

    def runAlgorithm(self, pod):
        """
        In time this will contain functions that determine the individual behaviour of each pod.
        """
        # Check the distance to destination. If it is too low then disable buddying
        if(pod.calculateRouteDistanceRemaining() < config.swarmMinBuddyingDistance):
            pod.buddyingAllowed = False
