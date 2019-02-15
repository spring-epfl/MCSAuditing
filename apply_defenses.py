import gc
import os
import sys
import scipy.spatial
import cPickle as pickle
import multiprocessing as mp

from defense_mechanisms import *
from safecast_extra_functions import calc_avg, PreCompute
from utility_functions import radiocells_find_antenna
from region_extraction_functions import extract_region, compute_prior
from __init__ import (place,
                      polygon,
                      defenses_path, dataset_used,
                      DATA_PATH,
                      datapath_to_original_file,original_csv_file, priors_csv, priors_transformed_path)


polygon = polygon.buffer(0)  # fix minor issues with the polygons
print place

if 'World' not in place:
    print polygon.is_valid  # check if the supplied polygon is valid


def apply_mechanisms(preparations):
    ensure_dir(DATA_PATH)
    dataset = place

    # the list with the mechanisms to be applied
    # and their parameters
    MECHANISMS = [('lap', 1.6, 0.05,0),  # params ==" name, lambda, epsilon, optimal remapping true/false"
                  ('lap', 1.6, 0.150,0),
                  ('lap', 1.6, 0.3,0),
                  ('geoindtraces', 1.6, 0.05, 30), # params ==" name, lambda, epsilon, radius"
                  ('geoindtraces', 1.6, 0.05, 60),
                  ('geoindtraces', 1.6, 0.05, 90),
                  ('release', 30),  # params ==" name, radius"
                  ('release', 60),
                  ('release', 90),
                  ('random', 40),   # params ==" name, percent"
                  ('random', 60),
                  ('random', 80),
                  ('rounding',2),   # params ==" name, rounding digits"
                  ('rounding',3),
                  ('rounding',4),
                  ('lap', 1.6, 0.05, 1),    # params ==" name, lambda, epsilon, optimal remapping true/false"
                  ('lap', 1.6, 0.15, 1),
                  ('lap', 1.6, 0.3, 1)]
#

#####################################################################
    # Do preparation stuff if specified
    if preparations:
        print dataset
        print ('Safecast' == dataset_used)
        print("Extracting region and applying filters")
        extract_region(original_csv_file,DATA_PATH, datapath_to_original_file,polygon, place)
        PreDestination_original = defenses_path  + dataset + "/"  # prepare path string
        ensure_dir(PreDestination_original)

        print('I will now create the priors')
        if os.path.isfile(priors_csv):
            compute_prior(priors_csv, priors_transformed_path)
            X = np.loadtxt(priors_transformed_path, skiprows=1, usecols=(0, 1), delimiter=",")
            # convert locations to cartesian using the center of the earth
            cartesianCoords = []
            print('Starting transforming to cartesian coordinates')
            for i in X:
                cartesianCoords.append(cartesian(i))
            cartesianCoords = np.asarray(cartesianCoords)
            tree = scipy.spatial.cKDTree(cartesianCoords, leafsize=4000)
            priorX = np.loadtxt(priors_transformed_path, skiprows=1, usecols=(2,), delimiter=",")
            priorX.shape = (priorX.shape[0], 1)  # priorX must be a matrix of one column
            print "Dumping stuff with pickle.."
            with open(DATA_PATH + 'priorX.pickle', 'wb') as handle:
                pickle.dump(priorX, handle)
            with open(DATA_PATH + 'KDtree.pickle', 'wb') as handle:
                pickle.dump(tree, handle)
            with open(DATA_PATH + 'X.pickle', 'wb') as handle:
                pickle.dump(X, handle)
        else:
            print('No priors file')

        if 'Safecast' == dataset_used:
            calc_avg(original_csv_file, PreDestination_original + dataset + ".avg.csv")
            print "Interpolating data..."
            PreCompute(PreDestination_original + dataset + ".avg.csv", PreDestination_original + dataset + ".pickle",
                       PreDestination_original + dataset + ".interpolated.csv", PreDestination_original + place + ".avg.csv")
        elif 'Radiocells' ==  dataset_used:
            radiocells_find_antenna(original_csv_file, PreDestination_original + dataset + ".avg.csv")
        else:
            print('No utility function selected')
        gc.collect()



    ######################################################################################################

    pool = mp.Pool(1)   #  Specify on how many cores this should happen
    funclist = []

    for df in MECHANISMS:
        print df
        f = pool.apply_async(parallel, [[df], defenses_path, datapath_to_original_file, DATA_PATH, PreDestination_original])
        funclist.append(f)

    result = []
    for f in funclist:
        result.append(f.get())

    return 0


def parallel(MECHANISMS, defenses_path, datapath_to_original_file, DATA_PATH, PreDestination_original ):

    DESTINATION = ""
    for mechanism in MECHANISMS:

        if mechanism[0] == 'rounding':
            method = mechanism[0]
            parameter = mechanism[1]
            print "\n Method: " + method + " Rounding to : " + str(parameter)+ " digits"
            # Calculate private data
            print "Calculating private data..."
            dataset = "rounded_" + str(parameter) + "_digits"  # e.g. osaka_rounded_5_digits
            PreDestination = defenses_path  + dataset + "/"
            ensure_dir(PreDestination)
            DESTINATION= PreDestination  + dataset +".csv"
            apply_rounding(datapath_to_original_file, DESTINATION, parameter)

        elif mechanism[0] == 'lap':

            method = mechanism[0]
            lamdaprv = math.log(mechanism[1])
            radius = mechanism[2]
            REMAPPING = mechanism[3]
            dataset = "geoind_lamda_" + str(mechanism[1]) + "_radius_"+ str(radius) +  "_method_" + method
            if REMAPPING:
                dataset += "_remapping"
                PreDestination = defenses_path + dataset + "/"
                ensure_dir(PreDestination)
                DESTINATION = PreDestination + dataset + ".csv"
                with open(DATA_PATH + 'X.pickle', 'rb') as handle:
                    X = pickle.load(handle)
                with open(DATA_PATH + 'priorX.pickle', 'rb') as handle:
                    priorX = pickle.load(handle)
                with open(DATA_PATH + 'KDtree.pickle', 'rb') as handle:
                    tree = pickle.load(handle)


                apply_geoind(datapath_to_original_file, DESTINATION, method, lamdaprv, radius, priorX, X,tree, 1)

            elif REMAPPING and ('Tokyo' not in place):
                return

            else:
                print 'Doing Geoind'
                PreDestination = defenses_path   + dataset + "/"
                ensure_dir(PreDestination)
                DESTINATION = PreDestination  + dataset + ".csv"
                apply_geoind(datapath_to_original_file, DESTINATION, method, lamdaprv, radius,  0, 0, 0)

        elif mechanism[0] == 'geoindtraces':
            method = mechanism[0]
            lamdaprv = math.log(mechanism[1])
            radius = mechanism[2]
            distance = mechanism[3]
            print "\n Method: " + method + " using  : " + str(distance) + " meters distance"
            # Calculate private data
            print "Calculating private data..."
            dataset = "geoind_traces_" + str(mechanism[1]) + "_radius_"+ str(radius) +  "_distance_" + str(distance)
            PreDestination = defenses_path   + dataset+ "/"
            ensure_dir(PreDestination)
            DESTINATION = PreDestination + dataset + ".csv"
            geoind_traces(datapath_to_original_file, DESTINATION, lamdaprv, radius, distance)

        elif mechanism[0] == 'random':
            method = mechanism[0]
            perc = mechanism[1]
            print "\n Method: " + method + " using  : " + str(perc) + " percent"
            # Calculate private data
            print "Calculating private data..."
            dataset = "random_sample_" + str(perc) + "_percent"  # e.g. osaka_rounded_5_digits
            PreDestination = defenses_path   + dataset+ "/"
            ensure_dir(PreDestination)
            DESTINATION = PreDestination + dataset + ".csv"
            apply_random_percent(datapath_to_original_file, DESTINATION, perc)

        elif mechanism[0] == 'release':
            method = mechanism[0]
            step = mechanism[1]
            print "\n Method: " + method + " using  : " + str(step) + " meters as step"
            # Calculate private data
            print "Calculating private data..."
            dataset = "spacex_" + str(step) + "_meters"  # e.g. osaka_rounded_5_digits
            PreDestination = defenses_path + dataset + "/"
            ensure_dir(PreDestination)
            DESTINATION = PreDestination + dataset + ".csv"
            apply_space_x(datapath_to_original_file, DESTINATION, float(step))
        else:
            print "Something wrong"
            exit(-1)

        if 'Safecast' == dataset_used:
            calc_avg(DESTINATION, PreDestination + dataset + ".avg.csv")
            print "Interpolating data..."
            PreCompute(PreDestination + dataset + ".avg.csv", PreDestination + dataset + ".pickle",
                       PreDestination + dataset + ".interpolated.csv", PreDestination_original + place + ".avg.csv")
        elif 'Radiocells' == dataset_used:
            radiocells_find_antenna(DESTINATION, PreDestination + dataset + ".avg.csv")
        else:
            print('No utility function selected')
        gc.collect()
    return 0


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


if __name__ == "__main__":
    # parse command line argument to figure out whether or not to filter the original safecast CSV
    do_preparation = False
    if len(sys.argv) > 1:
        do_preparation = (sys.argv[1] == "--do_preparation")
    apply_mechanisms(do_preparation)
