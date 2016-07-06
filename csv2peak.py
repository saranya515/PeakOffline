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
traffic = pd.read_csv('traffic_wix_MayJun2016.csv')
traffic.date_created = traffic.date_created.apply(lambda x: pd.Timestamp(x))


# SPOTS
spots = pd.read_excel('2016 06 28 EP WIX ALL FLIGHTS DE Malte Tool.xls')
spots.Datum = spots.Datum.map(lambda x: x.date())
spots['Timestamp'] = spots.Datum.combine(spots.Sendezeit, func=dt.datetime.combine)
spots['Timestamp'] = spots.Timestamp.apply(lambda x: x.replace(second=0))           # truncate seconds
spots['spot_id'] = spots.index + 1                                                  # spot id for peaks


## DO PEAK MEASUREMENT SE Style
t1 = dt.datetime.now()
traffic['baseline'] = traffic['anon_count'].rolling(center=True,window=41).median()
traffic['gross_uplift'] = 0
traffic.loc[traffic.anon_count > traffic.baseline * 1.6, 'gross_uplift'] = traffic.anon_count - traffic.baseline
print(dt.datetime.now() - t1)

#### CREATE PEAK DETAILS
t1 = dt.datetime.now()
peak_details = pd.DataFrame()

for s in list(range(len(spots))):
    # pick spot
    tmp_df = spots.iloc[s, ]                                                
    
    # Check whether traffic data is available,match spot time and traffic, extract ten minutes
    # if tmp_df.Timestamp not in list(traffic.date_created):    
    if len(traffic.loc[traffic.date_created == tmp_df.Timestamp]) == 0:
        continue
    
    time_index = traffic.index[traffic.date_created == tmp_df.Timestamp][0]
    traffic_slice = traffic.iloc[time_index:(time_index + 10),]  
    
    # create peak detail record
    traffic_slice['spot_id'] = tmp_df.spot_id                           
    traffic_slice['reach'] = tmp_df.KTS
    peak_details = peak_details.append(traffic_slice)

print(dt.datetime.now() - t1)
peak_details.reach.loc[peak_details.reach == 0] = 0.001 # set zero reach to 0.001

#### COMPUTE TOTAL AUDIENCE AND NET UPLIFT
total_audience_per_minute = peak_details.groupby(['date_created'])['reach'].sum().reset_index()         # sum reach for overlaps
peak_details = pd.merge(peak_details, total_audience_per_minute, how='left', on=['date_created'])           
peak_details['net_uplift'] = peak_details.gross_uplift * (peak_details.reach_x / peak_details.reach_y)  # compute net_uplift
sum_uplifts = peak_details.groupby(['spot_id'])['gross_uplift', 'net_uplift'].sum().reset_index()       # sum up by spot

# Insert data into spots sheet
spots = pd.merge(spots, sum_uplifts, how='inner', on=['spot_id'])

# spots.Sendezeit = spots.Sendezeit.astype(str)
spots = spots.loc[:,['Timestamp', 'Sender', 'Sendung', 'Kosten', 'Motiv', 'KTS', 'gross_uplift','net_uplift']]
spots.to_excel('Wix_MayJun2016_Uplift.xls', index=False)