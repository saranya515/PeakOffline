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

def generate_missing_minutes(df):
    '''Genereates missing minutes of zero traffic for the traffic data of one campaign'''
    ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), max(df.date_created), freq='1Min')})
    df = pd.merge(ts, df, how='left', on='date_created')
    df.anon_count = df.anon_count.fillna(0) 
    return df



## later read in from command line in __main__
traffic = pd.read_csv('FR_tv_anonymous_per_minute_2016-06-07.csv')
traffic = traffic.loc[traffic.country_code == 'DE'] # filter by country 

spots = 's'


# convert timestamp
traffic['date_created'] = traffic.date_created.apply(lambda x: pd.to_datetime(x))
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

peak_details = pd.DataFrame()
### for all spots
# slice ten minutes from traffic starting at spot data  merge
#ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), + 10 max(df.date_created), freq='1Min')})
# group by minute to get total reach... multiply with gross_uplift bang