import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from __init__ import RADIANT_TO_KM_CONSTANT



def attackscript(minpoints, mindistance, maxpois, coords,coords_with_date):
    if len(coords) == 0:
        print "No coords found :/"
        exit(-1)
    mindistance = mindistance / 1000.0  # necessary for the calculation in meters
    epsilon = mindistance / RADIANT_TO_KM_CONSTANT
    # This part can be changed to whatever the user prefers.
    # in this scenario we use the dbscan
    cluster_labels = dbscan(epsilon, minpoints, coords)
    try:
        num_clusters = len(set(cluster_labels))  # get the number of clusters
        if num_clusters == 1 or num_clusters ==0:
            return 0, 0
        else:
            clusters_with_date = pd.Series(
                sorted([coords_with_date[cluster_labels == n] for n in range(0, min(maxpois, num_clusters - 1))],
                       key=lambda x: len(x), reverse=True))

            return clusters_with_date, num_clusters
    except TypeError:
        return 0,0

def dbscan(epsilon, minpoints, coords):
    db = DBSCAN(eps=epsilon, min_samples=minpoints, algorithm='ball_tree', metric='haversine', leaf_size=100).fit(
        np.radians(coords))
    return  db.labels_  # get the label on which cluster every point belongs to


