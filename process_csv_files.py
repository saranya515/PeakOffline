# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 12:11:22 2016

Process csv files from wix.com

@author: matthiasgloel
"""
import os
import glob
import pandas as pd
import datetime as dt

# set path to one of script, keep spoteffects data in same folder
abspath = os.path.abspath('process_csv_files.py')
dname = os.path.dirname(abspath)
os.chdir(dname)

def generate_missing_minutes(df):
    '''Genereates missing minutes of zero traffic for the traffic data of one campaign'''
    ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), max(df.date_created), freq='1Min')})
    df = pd.merge(ts, df, how='left', on='date_created')
    df.anon_count = df.anon_count.fillna(0) 
    return df

## Reformat data of 2015 
all_files = glob.glob("/Users/matthiasgloel/PeakOffline/2015 campaigns/*.csv")     # advisable to use os.path.join as this makes concatenation OS independent
df = pd.concat(pd.read_csv(f, sep='\t', header=None) for f in all_files) 

df.columns = ['country_code', 'nul', 'channel', 'date_created', 'url', 'anon_count', 'newsletter', 'fil_ter']

# Filter by country, channel and mysterios column H == 1
df = df.query("country_code == 'DE' ")
df = df.loc[df['channel'].isin(['direct', 'organic', 'ppw_wix', 'seo'])]
df = df.query("fil_ter == 1")

# Drop redundant columns
df = df.drop(['nul','newsletter','fil_ter', 'channel','url'],1)
df = df.groupby(['date_created'])['anon_count'].sum().reset_index()

df['date_created'] = df.date_created.apply(lambda x: pd.to_datetime(x))

## Load data of 2016
afiles = glob.glob("/Users/matthiasgloel/PeakOffline/2016 campaigns/*.csv")
df2 = pd.concat(pd.read_csv(f, sep=',') for f in afiles) 

test = pd.read_csv("/Users/matthiasgloel/PeakOffline/2015 campaigns/2015-06-03(fr_tv_campaign_without_premiums) copy.csv", sep="\t", parse_dates = True)

# Filter by country, channel and mysterios column H == 1
df2 = df2.query("country_code == 'DE' ")
df2 = df2.loc[df2['channel'].isin(['direct', 'organic', 'ppw_wix', 'seo'])]
df2 = df2.drop(['device_type', 'channel'], 1)

df2 = df2.groupby(['date_created'])['anon_count'].sum().reset_index()


### generate missing minutes
df = generate_missing_minutes(df)
df2 = generate_missing_minutes(df2)

## merge df and df2, convert time string to datetime
dF = df.append(df2).reset_index()
dF['date_created'] = dF.date_created.apply(lambda x: pd.to_datetime(x))

a = pd.tslib.Timestamp('2016-02-15 00:01:00') 
b = pd.tslib.Timestamp('2016-05-15 23:59:00')
# filter out month march april
dF = dF.loc[(dF['date_created'] < a) | (dF['date_created'] > b)]

dF.to_csv('traffic_wix.csv')