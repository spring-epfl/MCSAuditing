import os
import numpy as np
import pandas as pd
import multiprocessing

from functools import partial
from shapely.geometry import Point

pd.options.mode.chained_assignment = None  # default='warn'


################################################
##
## Functions to pre process the large csv
##  limit the coordinates
##
##
################################################
def extract_region(OriginCsv, DATA_PATH, DESTINATION_DEFENSES, polygon, place):
    print "Removing previous file"
    if os.path.isfile(DESTINATION_DEFENSES):
        os.remove(DESTINATION_DEFENSES)

    if os.path.isfile(DATA_PATH + "wholeArea.csv"):
        os.remove(DATA_PATH + "wholeArea.csv")

    tmp = []
    cnt = 0
    # read the file in chunks
    # otherwise it may fill the whole ram
    for chunk in pd.read_csv(OriginCsv, iterator = True, chunksize=1000000):
        #if cnt % 5 == 0:
            #print cnt,'out of ', 64000000/1000000
        tmp.append(applypolygon(chunk,polygon,place))
        cnt += 1
    df = pd.concat(tmp,ignore_index= True)
    print 'Read original csv'
    df = funcusers(df, DATA_PATH, polygon,place)
    df.to_csv(DESTINATION_DEFENSES, index=False)
    return 0


def funcusers(df, DATA_PATH, polygon,place):
    # first create the file with the whole place area
    print 'will now try to parallelize'
    dfwholeplace = parallelize_dataframe(df, applypolygon, polygon, place)
    if not os.path.isfile(DATA_PATH + "wholeArea.csv"):
        dfwholeplace.to_csv(DATA_PATH + "wholeArea.csv", header='column_names', index=False)
    else:  # else it exists so append without writing the header
        dfwholeplace.to_csv(DATA_PATH + "wholeArea.csv", mode='a', header=False, index=False)
    return dfwholeplace


###################################
# When dataframes a too large
# we can parallelize
#
##################################
def parallelize_dataframe(df, func, poly,place):

    df_split = np.array_split(df, multiprocessing.cpu_count()-1)
    print 'Original file split'
    pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
    print "im working on {} cores".format(multiprocessing.cpu_count()-1)
    applypolygon_partial = partial(func, polygon=poly, place=place)
    #print "partial was successful"
    tmp = []
    tmp.append(pool.map(applypolygon_partial, df_split))
    df = pd.concat(tmp[0], ignore_index=True)
    pool.close()
    pool.join()
    return df


#############################################
# Return only coordinates within a polygon
# If World is selected, return all
#
#
#############################################
def applypolygon(dfmini,polygon, place):
    #print "here!!"
    dfmini = dfmini.dropna(axis=0, subset=['offset'])
    if 'World' not in place:
        dfmini = dfmini[dfmini.apply(lambda row: Point(row['Latitude'], row['Longitude']).within(polygon), axis=1)]
    return dfmini


#########################################
# Computs the prior probability of a file
#
########################################
def compute_prior(SOURCE_DATA, PRIORS_PATH):
    #We will calculate the probability of a user being at a
    #certain location
    df = pd.read_csv(SOURCE_DATA, error_bad_lines = False)
    df['Latitude'] = df['Latitude'].apply(lambda x: round(x, 3))
    df['Longitude'] = df['Longitude'].apply(lambda x: round(x, 3))
    dfprob = df.groupby(['Latitude', 'Longitude']).size().reset_index().rename(columns={0: 'PriorX'})
    dfprob['PriorX'] = dfprob['PriorX'] / dfprob['PriorX'].sum()
    dfprob = dfprob.drop_duplicates()
    dfprob.to_csv(PRIORS_PATH, index=False)
