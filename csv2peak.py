# -*- coding: utf-8 -*-
"""

csv2peak.py 

Input: Traffic and spot schedules as CSV

Output: Spreadsheet with NetUplift Per Spot

Created on Mon Jun 27 17:44:38 2016

@author: matthiasgloel
"""

import pandas as pd
import datetime as dt
import os

# set path to one of script, keep spoteffects data in same folder
abspath = '/Users/matthiasgloel/PeakOffline/'
os.chdir(abspath)

def generate_missing_minutes(df):
    '''Genereates missing minutes of zero traffic for the traffic data of one campaign'''
    ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), max(df.date_created), freq='1Min')})
    df = pd.merge(ts, df, how='left', on='date_created')
    df.anon_count = df.anon_count.fillna(0) 
    return df



## later read in from command line in __main__
#traffic = pd.read_csv('FR_tv_anonymous_per_minute_2016-06-07.csv')
#traffic = traffic.loc[traffic.country_code == 'DE'] # filter by country 
traffic = pd.read_csv('traffic_wix.csv')
traffic.date_created = traffic.date_created.apply(lambda x: pd.to_datetime(x))


# SPOTS
spots = pd.read_excel('2016 06 28 EP WIX ALL FLIGHTS DE Malte Tool.xls')
spots.Datum = spots.Datum.map(lambda x: x.date())
spots['Timestamp'] = spots.Datum.combine(spots.Sendezeit, func=dt.datetime.combine)
spots['Timestamp'] = spots.Timestamp.apply(lambda x: x.replace(second=0))           # truncate seconds
spots['spot_id'] = spots.index + 1                                                  # spot id for peaks

# generate missing minutes
## DO PEAK MEASUREMENT
# SE Style
t1 = dt.datetime.now()
traffic['baseline'] = traffic['anon_count'].rolling(center=True,window=41).median()
traffic['gross_uplift'] = 0
traffic.loc[traffic.anon_count > traffic.baseline * 1.6, 'gross_uplift'] = traffic.anon_count - traffic.baseline
print(dt.datetime.now() - t1)

#### CREATE PEAK DETAILS
t1 = dt.datetime.now()
peak_details = pd.DataFrame()
### for all spots
for s in list(range(len(spots))):
    tmp_df = spots.iloc[s, ]                                                # pick spot
     
    # Check whether traffic data is available,match spot time and traffic
    if tmp_df.Timestamp in traffic.date_created:
        time_index = traffic.index[traffic.date_created == tmp_df.Timestamp][0]
        traffic_slice = traffic.iloc[time_index:(time_index + 10),]  
    else:
        next           
    
    traffic_slice['spot_id'] = tmp_df.spot_id                           # create peak detail record
    traffic_slice['reach'] = tmp_df.KTS
    peak_details = peak_details.append(traffic_slice)
print(dt.datetime.now() - t1)





# slice ten minutes from traffic starting at spot data  merge
#ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), + 10 max(df.date_created), freq='1Min')})
# group by minute to get total reach... multiply with gross_uplift bang