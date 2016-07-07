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
traffic = pd.read_csv('traffic_wix_JanFeb2016.csv')
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
spots = spots.loc[:,['spot_id','Timestamp', 'Sender', 'Sendung', 'Kosten', 'Motiv', 'KTS', 'gross_uplift','net_uplift']]
#spots.to_excel('Wix_MayJun2016_Uplift.xls', index=False)


#### 
from ggplot import *
spotids = peak_details.spot_id.unique()
#2866
for s in spotids: 
    data = peak_details.loc[peak_details.spot_id == s]
    
    plt1 = ggplot(data, aes(x='date_created', y='anon_count'))
    plt1 += geom_line(aes(y='anon_count'),size=3)
    plt1 += geom_line(aes(y='baseline'), color='blue',size=2)
    plt1 += geom_line(aes(y=data.baseline * 1.6), color='red',size=2)
    plt1 += geom_point()
    plt1 += xlab('Minutes') 
    plt1 += ylab('Unique Visitors') 
    plt1 += theme_seaborn()
    plt1 += theme(axis_text_x  = element_text(size=16)) 
    plt1 += theme(axis_title_x  = element_text(size=22)) 
    plt1 += theme(axis_text_y  = element_text(size=16)) 
    plt1 += theme(axis_title_y  = element_text(size=22))
    plt1 += theme(plot_title  = element_text(size=26))
    plt1 += scale_x_date(labels = date_format("%H:%M"))
    plt1 += ggtitle('10 Minutes Immediately After Spot Airing: ' + str(s))
    #for m in len(data):
    #print(plt1)
    ggsave("./PeakDetailPlots/"+str(s)+"_pd.pdf",plot=plt1)

#ggplot(data, aes(x='date_created',y='anon_count')) +\
#    geom_point()
#print(plt1)
#print(plt)
        