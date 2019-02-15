import time
import os
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt

from scipy.interpolate import griddata
from shapely.geometry import Point
from shapely.ops import cascaded_union
from functools import partial
import multiprocessing
pd.options.mode.chained_assignment = None  # default='warn'


# Calculate average for same x/y coordiantes
def calc_avg(inputname, output):
    df = pd.read_csv(inputname)
    df['Latitude'] = df['Latitude'].apply(lambda x: round(x, 6))
    df['Longitude'] = df['Longitude'].apply(lambda x: round(x, 6))
    ss = df[['Latitude', 'Longitude', 'Value']].groupby(by=['Latitude', 'Longitude']).agg(['mean','count']).reset_index()
    ss.columns = ['lat_avg','lon_avg','cpm_avg','n']
    ss.to_csv(output, index=False)
    return 0


def LoadSafecastData(filename, CPMclip, latmin, latmax, lonmin, lonmax):
    # Load data

    data = csv.reader(open(filename))
    # Read the column names from the first line of the file
    fields = data.next()
    x = []
    y = []
    z = []
    zraw = []
    # Process data
    for row in data:
      # Zip together the field names and values
      items = zip(fields, row)
      # Add the value to our dictionary
      item = {}
      for (name, value) in items:
         item[name] = value.strip()

      # Ignore if outside limits
      if not ((float(item["lat_avg"])>latmin) and (float(item["lat_avg"])<latmax) and (float(item["lon_avg"])>lonmin) and (float(item["lon_avg"])<lonmax)):
        continue

      cpm = float(item["cpm_avg"])
      zraw.append(cpm)

      if cpm>CPMclip: cpm=CPMclip # clip

      x.append(float(item["lon_avg"]))
      y.append(float(item["lat_avg"]))
      z.append(float(cpm))

    npts = len(x)
    print "%s measurements loaded." % npts

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    zraw = np.array(zraw)

    return npts, x, y, z, zraw


def PreCompute(safecastDataset, output, output_csv,original, safecastDatasetCPMThreashold=20000, safecastGridsize=1500):
    # Setup: loading data...
    #print safecastDataset

    nx, ny = safecastGridsize, safecastGridsize # grid size


    original_df = pd.read_csv(original)

    latmin = original_df['lat_avg'].min()
    latmax = original_df['lat_avg'].max()
    lonmin = original_df['lon_avg'].min()
    lonmax = original_df['lon_avg'].max()
    print safecastDataset
    print latmin, latmax, lonmin, lonmax




    npts, x, y, z, zraw = LoadSafecastData(safecastDataset, safecastDatasetCPMThreashold, latmin, latmax, lonmin, lonmax)

    # Compute area with missing data
    print "Compute area with missing data"
    start  = time.time()
    measures = np.vstack((x,y)).T
    print "Time to vpstack: ", time.time() - start
    #start  = time.time()
    #points = [Point(a,b) for a, b in measures]
    #print "Time to points: ", time.time() - start
    #start  = time.time()
    #spots = [p.buffer(0.04) for p in points] # 0.04 degree ~ 1km radius
    #print "Time to spots: ", time.time() - start
    #start  = time.time()
    ## Perform a cascaded union of the polygon spots, dissolving them into a
    ## collection of polygon patches
#
    #missing = cascaded_union(spots)
    #print "Time to cascade union: ", time.time() - start

    # Create the grid
    print "Create the grid"
    #xil = np.linspace(x.min(), x.max(), nx)
    #yil = np.linspace(y.min(), y.max(), ny)

    xil = np.linspace(lonmin, lonmax, nx)
    yil = np.linspace(latmin, latmax, ny)
    xi, yi = np.meshgrid(xil, yil)

    ## Attention, even though it says nearest, we calculate the linear as its waaay faster

    # Calculate the griddata
    print "Calculate the griddata (%d x %d)" % (nx, ny)
    t1 = time.clock()
    try:
        zi = griddata(measures, z, (xi, yi), method='nearest') # Original: interp='nn'
    except RuntimeError as e:
        print e
        print "x: " + str(x) + "y: " + str(y) + "z: " + str(z)

    grid = zi.reshape((ny, nx))
    print "Interpolation done in",time.clock()-t1,'seconds.'

    #toSave = [npts, x, y, z, zraw, xil, yil, grid, missing]
    #cPickle.dump(toSave,open(output,'wb'),-1)
    #print "Griddata saved (" + output + ")."
    #print "Also save grid as csv for utility calculation"
    out = csv.writer(open(output_csv, 'wb'))
    out.writerows(grid)
    print "Griddata saved as csv (" + output_csv + ")."

    return 0


def radiocells_find_antenna(path, utility_path):

    df = pd.read_csv(path, dtype = {'mcc': str, 'mnc': str})
    dutility = df.groupby(['mcc', 'mnc', 'lac', 'Cellid'])['Latitude', 'Longitude'].mean().reset_index()
    dutility.to_csv(utility_path, index=False)
    return




