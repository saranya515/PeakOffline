# -*- coding: utf-8 -*-
"""

csv2peak.py 

Input: Traffic and spot schedules as CSV

Output: Spreadsheet with NetUplift Per Spot

Created on Mon Jun 27 17:44:38 2016

@author: matthiasgloel
"""

import pandas as pd

## later read in from command line in __main__
traffic = pd.read_csv('FR_tv_anonymous_per_minute_2016-06-07.csv')

traffic['date_created'] = traffic.date_created.apply(lambda x: pd.to_datetime(x))
traffic = traffic.sort_values(by = ['country_code','date_created'])

# aggregate over minutes... split?
traffic_agg = traffic.groupby(['country_code', 'date_created'])['anon_count'].sum().reset_index()

# generate missing minutes
