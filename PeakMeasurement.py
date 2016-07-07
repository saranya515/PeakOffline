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
    
    def __init__(self, baseline_window = 41, peak_window = 10):
       # self.spots = spots                           # timestamps and reach + opts
       # self.traffic = traffic                       # timestamps and count + opts
        self.baseline_window = baseline_window       # timewindow of baseline calculation
        self.peak_window = peak_window               # allocation window to detect peaks
        self.peak_details = pd.DataFrame()           # for plotting
        self.uplift_table = pd.DataFrame()
    
    def calculate_se(self, traffic, spots):
        ## DO PEAK GROSS UPLIFT SE Style
        traffic['baseline'] = traffic['anon_count'].rolling(center=True,window=41).median()
        traffic['gross_uplift'] = 0
        traffic.loc[traffic.anon_count > traffic['baseline'] * 1.6, 'gross_uplift'] = traffic.anon_count - traffic.baseline
    
        #peak_details = pd.DataFrame()
        for s in list(range(len(spots))):
            tmp_df = spots.iloc[s, ]                                                
            
            # Traffic data around spot available    
            if len(traffic.loc[traffic.date_created == tmp_df.Timestamp]) == 0:
                continue
            # Yes. Extract ten minutes
            time_index = traffic.index[traffic.date_created == tmp_df.Timestamp][0]
            traffic_slice = traffic.iloc[time_index:(time_index + 10),]  
            
            # create peak detail record
            traffic_slice['spot_id'] = tmp_df.spot_id                           
            traffic_slice['reach'] = tmp_df.KTS
            self.peak_details = self.peak_details.append(traffic_slice)
        
        # set zero reach to 0.001
        self.peak_details.reach.loc[self.peak_details.reach == 0] = 0.001 
        
        # DO NET UPLIFT WEIGHTED BY REACH
        total_audience_per_minute = self.peak_details.groupby(['date_created'])['reach'].sum().reset_index()         
        self.peak_details = pd.merge(self.peak_details, total_audience_per_minute, how='left', on=['date_created'])       
        self.peak_details['net_uplift'] = self.peak_details.gross_uplift * (self.peak_details.reach_x / self.peak_details.reach_y)  
        sum_uplifts = self.peak_details.groupby(['spot_id'])['gross_uplift', 'net_uplift'].sum().reset_index()     
        
        # Insert data into spots sheet
        output = pd.merge(spots, sum_uplifts, how='inner', on=['spot_id'])
        
        return output
                
        
    def calculate_dcmn(self):
        return self
        
    def generate_missing_minutes(self, df):
        '''Genereates missing minutes of zero traffic for the traffic data of one campaign'''
        ts = pd.DataFrame({'date_created' : pd.date_range(min(df.date_created), max(df.date_created), freq='1Min')})
        df = pd.merge(ts, df, how='left', on='date_created')
        df.anon_count = df.anon_count.fillna(0) 
        return df 