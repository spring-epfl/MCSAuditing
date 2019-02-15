import pandas as pd

from __init__ import starttime, endtime,place

pd.options.mode.chained_assignment = None  # default='warn'

####################################
# filters the dataset and applies the offset
# required for most types of operations that involve time
#
#
def preprocess(dfmain):

    #if 'World' not in place:
    dfmain['Captured Time'] = pd.to_datetime(dfmain['Captured Time'], format='%Y-%m-%d %H:%M:%S')
    df = dfmain[((pd.to_datetime(dfmain['Captured Time']) + (
                        pd.to_timedelta(dfmain['offset'] / 60, unit='h'))).dt.hour > starttime) &
                                ((pd.to_datetime(dfmain['Captured Time']) + (
                                pd.to_timedelta(dfmain['offset'] / 60, unit='h'))).dt.hour < endtime) &
                                ((pd.to_datetime(dfmain['Captured Time']) + (
                                pd.to_timedelta(dfmain['offset'] / 60, unit='h'))).dt.dayofweek < 5)]
 
    return df
