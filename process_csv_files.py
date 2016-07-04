# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 12:11:22 2016

Process csv files from wix.com

@author: matthiasgloel
"""
import os
import glob
import pandas as pd
# set path to one of script, keep spoteffects data in same folder
abspath = os.path.abspath('process_csv_files.py')
dname = os.path.dirname(abspath)
os.chdir(dname)

all_files = glob.glob("/Users/matthiasgloel/PeakOffline/2015 campaigns/*.csv")     # advisable to use os.path.join as this makes concatenation OS independent
df = pd.concat(pd.read_csv(f, sep='\t', header=None) for f in all_files) 

alldfs = []
lensen = []
for f in all_files:
    c = pd.read_csv(f, sep='\t', header=None)
    alldfs.append(c)
    lensen.append(c.shape[1])
    
df.columns = ['country', 'nul', 'channel', 'timestamp', 'url', 'anon_count', 'newsletter', 'fil_ter']

df = df.query("country == 'DE' ")
df = df.loc[df['channel'].isin(['direct', 'organic', 'ppw_wix', 'seo'])]
df = df.query("fil_ter == 1")

