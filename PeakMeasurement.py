# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 12:14:00 2016

@author: matthiasgloel


"""
import pandas as pd
import datetime as dt

class PeakMeasurement:
    """
    Peak measurement takes spots and traffic and does uplift calculation
    """
    
    def __init__(self, spots, traffic):
        
        self.spots = spots
        self.traffic = traffic
        

    