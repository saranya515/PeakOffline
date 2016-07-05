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
spots = pd.read_excel('2016 06 28 EP WIX ALL FLIGHTS DE Malte Tool.xls', parse_dates = [['Datum','Sendezeit']])
spots.Datum = spots.Datum.map(lambda x: x.date)
spots.Timestamp = spots.Datum.combine(spots.Sendezeit, func=dt.datetime.combine)


# convert timestamp
traffic['date_created'] = traffic.date_created.apply(lambda x: x.to_datetime())
traffic = traffic.sort_values(by = ['country_code','date_created'])

# aggregate over minutes
traffic_agg = traffic.groupby(['country_code', 'date_created'])['anon_count'].sum().reset_index()
traffic_agg = generate_missing_minutes(traffic_agg)
traffic_agg.country_code = 'DE'


# generate missing minutes
## DO PEAK MEASUREMENT
# SE Style
t1 = dt.datetime.now()
traffic_agg['baseline'] = traffic_agg['anon_count'].rolling(center=True,window=41).median()
traffic_agg['gross_uplift'] = 0
traffic_agg.loc[traffic_agg.anon_count > traffic_agg.baseline * 1.6, 'gross_uplift'] = traffic_agg.anon_count - traffic_agg.baseline
print(dt.datetime.now() - t1)


## Create Peaks Details table based on spots
rnd_time = traffic_agg.date_created[600]
spots = pd.DataFrame([{'spot_id' : 1 ,'minute' : rnd_time, 'reach' : 1000}])

peak_details = pd.DataFrame()
### for all spots
for s in list(range(len(spots))):
    # first slice traffic create tmpd_ df... append to peak details    
    tmp_df = spots.iloc[s, ]
    # find minute of spot in traffic data
    time_index = traffic_agg.index[traffic_agg.date_created == tmp_df.minute][0]
    traffic_slice = traffic_agg.iloc[time_index:(time_index + 10),]
    #merge spot with 10 min traffic window
    # tmp_df = pd.merge(tmp_df, traffic)
    traffic_slice.loc['spot_id'] = tmp_df.spot_id
    traffic_slice.loc[:,'reach'] = tmp_df.reach
    peak_details.append(traffic_slice)
# slice ten minutes from traffic starting at spot data  merge
#ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), + 10 max(df.date_created), freq='1Min')})
# group by minute to get total reach... multiply with gross_uplift bang