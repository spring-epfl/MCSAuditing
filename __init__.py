from getJson import  *
from shapely.geometry import Point, Polygon

RADIANT_TO_KM_CONSTANT = 6371.0088

cfg = get()

# Get all json values
place = cfg['place']
dataset_used = cfg['dataset_used']
polygon = Polygon(cfg['Polygon'])
minpoints = int(cfg['minpoints'])
maxdistance = float(cfg['maxdistance'])
maxpois = int(cfg['maxpois'])
starttime = int(cfg['starttime'])
endtime = int(cfg['endtime'])
advanced_clustering = int(cfg['advanced_clustering'])
min_allowed_points = int(cfg['min_allowed_points'])
max_allowed_distance = int(cfg['max_allowed_distance'])
original_min_points = int(cfg['original_min_points'])

#############################################
#
# Required paths  for applying defenses
#
############################################
mypath = "folder_of_the_project"
original_csv_file = "path_to_original_file_with_data" #  this file needs to be called original.csv
priors_csv = "path_to_data_priors" # this file needs to be called data_for_priors.csv

##################################################
#
# Better not to touch below this part
#
#
################################################
ORIGIN = mypath + "/data/"
DATA_PATH = ORIGIN + place + "/"

#The original file after we have extracted all coords in a polygon needs to be called 'for_defenses.csv',
# but feel free to change
datapath_to_original_file = ORIGIN + place + "/" + "for_defenses.csv"
priors_transformed_path = ORIGIN + place + "/" + "priors.csv"

defenses_path_place = mypath + "/defences/"+place+"/"
defenses_path = mypath + "/defences/"

# Required paths for privacyloss calculations
filespath = defenses_path

writeplace = place + '''{}_points_{}dist'''.format(int(minpoints), int(maxdistance))

if advanced_clustering == 1:
    writeplace = writeplace + '''_advancedClustering'''
else:
    writeplace = writeplace + '''_standardClustering'''

utilities_plot = mypath + "/plots/"
privacyloss_path = mypath + "/privacyloss/"
privacyloss_plots = privacyloss_path + "plots/"
DATA_BASE_WRITE_UTILITY = privacyloss_path + writeplace + "/"
original_pickle = privacyloss_path + "{}/original.pickle".format(writeplace)


def return_write_path(thisplace):

    writeplace = thisplace + '''{}_points_{}dist'''.format(int(minpoints), int(maxdistance))

    if advanced_clustering == 1:
        writeplace = writeplace + '''_advancedClustering'''
    else:
        writeplace = writeplace + '''_standardClustering'''

    return writeplace