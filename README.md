========== How to set the parameters the tool ===============

The main files that need tweaking are the 

__init__.py and
pipelineJson.json


################
__init__.py:

You have to change the path in the section "Required paths  for applying defenses".

mypath: the path to the folder of your project 

original_csv_file: the path to your dataset. This file *needs* to be called original.csv

priors_csv : the path to the dataset that will be used for calculating the prior probabilities of locations.
			 This file is relevant only for defenses that are augmented with optimal remapping.
			 This file *needs* to be called data_for_priors.csv



##################
pipelineJson.json

This file includes parameters abou the attacks, and the datasets used.

If you wand to run the tool on all of your dataset, then place *needs* to be call "World.".
Otherwise, you can change it to whatever you want however, then you need to specify a *valid* polygon for the extraction.

Detailed:

Place: World if no region extraction otherwise free to choose

dataset_used: the name of you dataset. In this tool, we provide two datasets and their utility functions. Those are the "Safecast" and 
"Radiocells" datasets. The variable name is case sensitive. If you specify your own dataset name, you will not be able to use the utility 
functions of these datasets. However, you can tweak the tool to include your own funtion.

minpoints: the DBSCAN's parameter minimum points

maxdistance: DBSCAN's parameter maximum distance among points

maxpois: The top N clusters that should be kept

starttime: Keep only measurement that start from this time

endtime: and end this time. Basically, the last two parameters filter the dataset.

advanced_clustering: Whether to use standard clustering parameters (value=0) or adjustable(value=1).

min_allowed_points: When using adjustable clustering, the minimum limit points are allowed to reach.

max_allowed_distance:  When using adjustable clustering, the maximum distance allowed.

original_min_points: When using adjustable clustering, the value can replace the initial minpoints.


Polygon: This *needs* to be a valid (closed) polygon and the edges need to be in the form of (latitude, longitude). 
See here for various polygons --> https://download.geofabrik.de/. 
However, the above link provides the polygons in the opposite order (longitude, latitude). If you use such polygons 
make sure you reverse the edges.



======== How to run the tool ==================

The main functions that automates everything is inside the
automated_pipeline.py file and is called runpipeline.

When you call runpipeline, the tool

first: 1) extracts the region, 
		2)computes the priors if any, 
		3)apply all defenses to the location data.
		The tool saves the defense files in a folder called defenses.


You can select which defenses you want in the file apply_defenses.py


second: the tool calculates all users original privacy in spatial terms and POIs.
		In order to do so, rellies on the attackscript inside the attackmodule.py. 
		If you wish to change the attackm, modify this file.

		In addition, the tool relies on OSM to collect POIs.
		Currently it uses a public server that if under load starts blocking requests.
		The tool has defenses for this and tries again after x seconds.
		However, you could also use your own OSM server by modifying the line
		api = overpy.Overpass(url='your url') inside the privacy_gain.py file.

		Then, the tool applies the attacks also on the defense files.
		All resulting files are pickled and saved in the privacyloss folder.

third: The tool, if Safecast or Radiocells are specified (and correct files are provided), calculates the utility loss.
		As the tool relies on a specific order of the files it finds, (the columns in the csv should be in specific order),
		we provide templates for the Radiocells and the Safecast datasets.
		The graphs are saved in the plots folder.


fourth: The tool calculates the privacy gains and plots it. Again, this is a demonstration on the datasets of the paper.
		The privacy gain folder with each user's privacy gain is saved in the privacyloss folder.
		The graphs however are stored in the plots folder.


		



