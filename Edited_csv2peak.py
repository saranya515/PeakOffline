"""
Imports should be grouped in the following order:

standard library imports
related third party imports
local application/library specific imports
"""
import os
import datetime as dt

import pandas as pd
import pytz

abspath = '/Users/saranyaks/Matthias/fork/PeakOffline/'
os.chdir(abspath)


def generate_missing_minutes(df):
    """
    function to do something..
    :param df:
    :return:
    """
    # TRAFFIC
    traffic = pd.read_csv('traffic_example.csv')
    traffic.date_created = traffic.date_created.apply(
        lambda x: pd.Timestamp(x))

    # SPOTS
    spots = pd.read_excel('2016 06 28 EP WIX ALL FLIGHTS DE Malte Tool.xls')
    spots.Datum = spots.Datum.map(lambda x: x.date())

    spots['Timestamp'] = spots.Datum.combine(
        spots.Sendezeit, func=dt.datetime.combine)

    # passing timestamp to add berlin time zone ,
    spots['Timestamp'] = add_timezone(spots.Timestamp)

    # converting to UTC time zone.
    spots['Timestamp'] = utc_timezone(spots.Timestamp)


def add_timezone(timestamp):
    """
    To add berlin time zone to date.
    """
    for i in xrange(len(timestamp)):
        naive_date = dt.datetime.strptime(timestamp[i], "%Y-%m-%d %H:%M:%S")
        localtz = pytz.timezone('Europe/Berlin')
        date_local = localtz.localize(naive_date)
        timestamp[i] = date_local
    return timestamp


def utc_timezone(timestamp):
    """
    To convert Berlin timezone to UTC.
    """
    for i in xrange(len(timestamp)):
        utc_date = timestamp[i].astimezone(pytz.utc)
        timestamp[i] = utc_date
    return timestamp
