import numpy as np
import math
import random
from numpy.random import random_sample
from scipy.special import lambertw
import pandas as pd
from cHaversine import haversine
from sklearn.metrics.pairwise import pairwise_distances
import time
import csv
from __init__ import RADIANT_TO_KM_CONSTANT
import threading

pd.options.mode.chained_assignment = None  # default='warn'

mylockprint = threading.RLock()

def printmsg(text):
    with mylockprint:
        print text
    return


###############################################################
#
# Apply privacy by simply rounding the coordinates to N_DIGITS
#
#
##############################################################
def apply_rounding(DATA_PATH, DESTINATION_ROUNDING, N_DIGITS):
    df = pd.read_csv(DATA_PATH)
    df = df.round({'Latitude': N_DIGITS, 'Longitude': N_DIGITS})
    # df.Latitude = df.Latitude*10000
    # df.Longitude = df.Longitude*10000 # we multiply with 10000 in order to save it as interger and not lose precission
    floatformat = '%.{}f'.format(N_DIGITS)
    df.to_csv(DESTINATION_ROUNDING, index=False, float_format=floatformat)

    return 0


def checkcoords(lat,lng):
    return (lat >=- 90 and lat <= 90) and ( lng >= -180 and lng <=180)


###############################################################
#
# Apply privacy by simply taking a random sub sample
#
#
##############################################################
def apply_random_percent(DATA_PATH, DESTINATION, perc):
    time.sleep(0.1)
    np.random.seed(None)
    random.seed(None)
    df = pd.read_csv(DATA_PATH)
    groups = df.sort_values(['User ID', 'Captured Time'])
    with open(DESTINATION, 'wb+') as writerlocation:
        writer_geoind = csv.writer(writerlocation, delimiter=",")
        writer_geoind.writerow(df.columns)
        for index, row in groups.iterrows():
            if flip_biased_coin(perc): writer_geoind.writerow(row.values)
    return 0


def flip_biased_coin(perc):
    return 1 if random.random() < perc/100. else 0


###############################################################
#
# Apply privacy by letting points have a distance of x meters
#
#
##############################################################
def apply_space_x(DATA_PATH, DESTINATION_SPACEX, desdistance):
    df = pd.read_csv(DATA_PATH)
    df = df.sort_values(by='Captured Time')
    grouped = df.groupby('User ID')
    tmpdf = []
    for name, group in grouped:
        tmpdf.append(spacex(group, desdistance))
    dfinal = pd.concat(tmpdf)
    dfinal.to_csv(DESTINATION_SPACEX, index=False)
    return 0


def spacex(dfmain, desdistance):
    # previous to next point only if in logical time and space
    place = zip(dfmain.Latitude.values, dfmain.Longitude.values)
    dates = dfmain['Captured Time'].values
    dates = pd.to_datetime(dates)
    keep = [0]
    i = 1
    while i < dfmain.__len__() - 1:
        if haversine(place[keep[-1]], place[i]) > desdistance or dates[keep[-1]].date() != dates[i].date():
            keep.append(i)
        i += 1

    if keep:np1 = np.array(keep)
    else : return

    return dfmain.iloc[np1]


#############################
# Geoind mechanism

def apply_geoind(DATA_PATH, DESTINATION_GEOIND, method, lamdaprv, radius, priorX, X,tree, OPTIMAL_REMAPPING):
    time.sleep(0.5)
    np.random.seed(None)  # required for initialazation
    epsilon = float(lamdaprv / radius)
    newradius = -1. / epsilon * (np.real(lambertw((0.99 - 1) / math.e, k=-1)) + 1)
    cartesianCoords = X
    nopoiscnt = 0

    with open(DATA_PATH, "rb") as openedata:  ## applies the noise in every line in the input file
        with open(DESTINATION_GEOIND, 'wb+') as writerlocation:
            startwhole = time.time()
            reader = csv.reader(openedata, delimiter=",")
            writer_geoind = csv.writer(writerlocation, delimiter=",")

            for i, line in enumerate(reader):
                startpoint = time.time()
                if i == 0:
                    # Skip the header line
                    writer_geoind.writerow(line)
                    continue
                try:
                    lat = float(line[3])
                    lng = float(line[4])
                    if not checkcoords(lat,lng): print "Wrong coordinates in the geoind", exit(-1)

                    # Apply geoind...
                    loc_original = np.array([lat, lng])  # original location
                    r, theta = compute_noise(epsilon)
                    loc_noise = addVectorToPos(loc_original, r, theta)

                    # ...with optimal remapping
                    if OPTIMAL_REMAPPING:
                        loc_noise_cartesian = cartesian(loc_noise)
                        index = tree.query_ball_point(loc_noise_cartesian, p=2.0, r=newradius)
                        if len(index) == 0:
                            nopoiscnt += 1
                            # print "No suitable point found around", loc_noise
                            loc_output = loc_noise
                            line[3] = round(loc_output[0], 5)
                            line[4] = round(loc_output[1], 5)
                            writer_geoind.writerow(line)
                            continue


                        distances = pairwise_distances([loc_noise_cartesian], cartesianCoords[index])
                        tmparray = np.zeros(shape=distances[0].shape)
                        dist1 = np.vstack((distances[0], tmparray))
                        startPost = time.time()
                        posteriorX = priorX[index] * np.exp(-epsilon * dist1.transpose())
                        sumPostX = np.copy(posteriorX[:, 1])
                        posteriorX = np.multiply(priorX[index],
                                                 np.exp(np.multiply(-epsilon, dist1.transpose())))

                        posteriorX = np.divide(posteriorX[:, 1], np.sum(sumPostX))

                        if np.sum(posteriorX) > 1.000000001 or np.sum(posteriorX) < 0.999999999:
                            print "posterior problem"

                        # print numpy.sum(posteriorX)
                        loc_optimal = compute_geometric_median(posteriorX[:], X[index])  # optimal remapping
                        if np.isnan(loc_optimal[0]) or np.isnan(loc_optimal[1]):
                            loc_output = loc_noise
                        else:
                            loc_output = loc_optimal

                    # ...without optimal remapping
                    else:
                        loc_output = loc_noise

                    # write output (with same precision as in original data)
                    line[3] = round(loc_output[0], 5)
                    line[4] = round(loc_output[1], 5)
        
                    writer_geoind.writerow(line)

                except Exception as e:
                    print("Error: line[{}]: {} ; {}".format(i, line, e))


def geoind_traces(data_path, destination_path, lamdaprv,radius, desdistance):
   time.sleep(0.2)
   np.random.seed(None)
   place_to_write = destination_path
   epsilon = float(lamdaprv / radius)
   df = pd.read_csv(data_path)
   groups = df.sort_values(['User ID', 'Captured Time'])
   with open(place_to_write, 'wb+') as writerlocation:
       writer_geoind = csv.writer(writerlocation, delimiter=",")
       writer_geoind.writerow(df.columns)
       last_user = -1
       last_lat = -1
       last_lon = -1
       last_noisy_lat = -1
       last_noisy_lon = -1

       for index, row in groups.iterrows():
           if row['User ID'] != last_user:
               last_user = row['User ID']
               last_lat = row['Latitude']
               last_lon = row['Longitude']
               row['Latitude'], row['Longitude'] = geo_ind(row['Latitude'], row['Longitude'], epsilon)
               last_noisy_lat = row['Latitude']
               last_noisy_lon = row['Longitude']
           elif haversine((last_lat, last_lon), (row['Latitude'], row['Longitude'])) > desdistance:
               flag = 1
               last_lat = row['Latitude']
               last_lon = row['Longitude']
               row['Latitude'], row['Longitude'] = geo_ind(row['Latitude'], row['Longitude'], epsilon)
               last_noisy_lat = row['Latitude']
               last_noisy_lon = row['Longitude']
           else:
               row['Latitude'], row['Longitude'] = last_noisy_lat, last_noisy_lon

           writer_geoind.writerow(row.values)


def geo_ind(lat, lon, epsilon):
    loc_original = np.array([lat, lon])  # original location
    r, theta = compute_noise(epsilon)
    loc_noise = addVectorToPos(loc_original, r, theta)
    return round(loc_noise[0], 5), round(loc_noise[1], 5)


#########################################
#
# Add the generated doise directly on the
# gps coordinates
#
#########################################
def addVectorToPos(pos, distance, angle):
    ang_distance = distance / RADIANT_TO_KM_CONSTANT
    lat1 = rad_of_deg(pos[0])
    lon1 = rad_of_deg(pos[1])

    lat2 = math.asin( math.sin(lat1) * math.cos(ang_distance) +
                    math.cos(lat1) * math.sin(ang_distance) * math.cos(angle))
    lon2 = lon1 +   math.atan2(
        math.sin(angle) * math.sin(ang_distance) * math.cos(lat1),
        math.cos(ang_distance) - math.sin(lat1) * math.sin(lat2) )
    lon2 = (lon2 + 3 * math.pi) % (2 * math.pi) - math.pi #normalise to -180..+180
    return deg_of_rad(lat2), deg_of_rad(lon2)


#############################################
#
# Usefule for the addVectorToPos function
#
############################################
def rad_of_deg(ang): return ang * math.pi / 180


def deg_of_rad(ang): return ang * 180 / math.pi


def compute_noise(param):
    epsilon = param
    theta = random_sample() * 2 * math.pi
    r = -1. / epsilon * (np.real(lambertw((random_sample() - 1) / math.e, k=-1)) + 1)
    return r, theta


def cartesian(coords):
    lat=np.radians(coords[0])
    lon=np.radians(coords[1])
    x = RADIANT_TO_KM_CONSTANT * np.cos(lat) * np.cos(lon)
    y = RADIANT_TO_KM_CONSTANT * np.cos(lat) * np.sin(lon)
    return np.array([x, y])


def compute_geometric_median(probabilities_input, values_input):
    # Computes the geometric median. Weiszfeld's algorithm
    probabilities = np.copy(probabilities_input)
    values = np.copy(values_input)

    values = values[probabilities > 0]  # remove entries of values with probability of 0
    probabilities = probabilities[probabilities > 0]  # remove zero entries
    geo_median_old = np.array([float("inf"), float("inf")])
    geo_median = np.dot(probabilities.transpose(), values)  # Initial estimation is the mean
    nIter = 0
    while (check_condition(geo_median, geo_median_old)) and (nIter < 200):

        distance_matrix = pairwise_distances([geo_median], values)
        distance_matrix = distance_matrix[0]
        # Return if there is a zero value in distance_matrix
        if np.any(distance_matrix == 0):
            #print "emerg brake", nIter
            return geo_median
        # print len(distance_matrix)
        geo_median_old = geo_median
        div = np.divide(probabilities, distance_matrix)
        geo_median = np.divide(np.dot(div, values), np.dot(div, np.ones_like(values)))
        nIter += 1
    return geo_median


def check_condition(geo_median, geo_median_old):
    return np.linalg.norm(geo_median - geo_median_old) > 1e-3
