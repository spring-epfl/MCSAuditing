import os
import re
import threading
import overpy
import time
import random
import multiprocessing
import cPickle as pickle

from attackmodule import *
from shapely.geometry import  Point, Polygon, MultiPolygon
from shapely.ops import cascaded_union
from mpl_toolkits.basemap import pyproj as pyproj
from preprocess_df import *
from multiprocessing import  Manager
from multiprocessing import freeze_support
#from multiprocessing import Manager, freeze_support
from functools import partial
from concurrent.futures import TimeoutError
from pebble import ProcessPool, ProcessExpired
from __init__ import (place,
                      minpoints, maxdistance,maxpois,starttime,endtime,original_min_points,
                      writeplace, defenses_path,DATA_BASE_WRITE_UTILITY, datapath_to_original_file,
                      advanced_clustering, min_allowed_points, max_allowed_distance)


def main_privacy_gain(arg):
    freeze_support()
    mylockcl = threading.RLock()
    mylockprint = threading.RLock()
    manager = Manager()
    api = overpy.Overpass()
    wgs84 = pyproj.Proj("+init=EPSG:4326")
    osm3857 = pyproj.Proj("+init=EPSG:3857")
    #dictd = manager.dict()
    dictd = {}

    def mainprivacyloss(initcalc):
        ensure_dir(DATA_BASE_WRITE_UTILITY)

        defs = ['geoind[1.6, 0.05]',
                'geoind[1.6, 0.15]',
                'geoind[1.6, 0.3]',
                'remap[1.6, 0.05]',
                'remap[1.6, 0.15]',
                'remap[1.6, 0.3]',
                'rnd_sample[40]',
                'rnd_sample[60]',
                'rnd_sample[80]',
                'rounded[3]',
                'rounded[2]',
                'rounded[4]',
                'geoind_traces[1.6, 0.05, 30.0]',
                'geoind_traces[1.6, 0.05, 60.0]',
                'geoind_traces[1.6, 0.05, 90.0]',
                'spacex[30.0]',
                'spacex[60.0]',
                'spacex[90.0]']


        #################
        ##
        ##  Calculate the original cluster polygons per user
        ##
        ##
        #######################
        existinglist = existingfiles()
        existinglist = [i.split('tmp')[0] for i in existinglist]

        if initcalc == 1: ## Calculate the original privacy for every user
            dfmain = pd.read_csv(datapath_to_original_file)
            print('read original')
            savedict(dfmain, 'original', starttime, endtime, minpoints, maxdistance, maxpois, 0,[])

        # Load users original privacy files
        if os.path.isfile(DATA_BASE_WRITE_UTILITY + 'original' + '.pickle'):
            with open(DATA_BASE_WRITE_UTILITY + 'original' + '.pickle', 'rb') as handle:
                original_users = pickle.load(handle)
                original_users = original_users.keys()
        else:
            print 'Could not load original privacy file'
            exit(-1)

        print "original users loaded"

        # For every defense file, calculate the privacy loss
        for root, dirs, files in os.walk(defenses_path):
            names = []
            if 'bak' in os.path.basename(root):continue  # check for old files

            if ("geoind" in os.path.basename(root)) and ('traces' not in os.path.basename(root)):
                params = [float(s) for s in re.findall(r'-?\d+\.?\d*', os.path.basename(root))]
                if "remapping" in os.path.basename(root):
                    keyword = "remap"+str(params)
                else:
                    keyword = "geoind"+str(params)

            elif "rounded" in os.path.basename(root):

                params = [int(s) for s in re.findall(r'-?\d+\.?\d*', os.path.basename(root))]
                keyword = "rounded"+str(params)

            elif "random" in os.path.basename(root):
                params = [int(s) for s in re.findall(r'-?\d+\.?\d*', os.path.basename(root))]
                keyword = "rnd_sample"+str(params)

            elif "spacex" in os.path.basename(root):
                params = [float(s) for s in re.findall(r'-?\d+\.?\d*', os.path.basename(root))]
                keyword = "spacex"+str(params)

            elif "traces" in os.path.basename(root):
                params = [float(s) for s in re.findall(r'-?\d+\.?\d*', os.path.basename(root))]
                keyword = "geoind_traces"+str(params)

            else:
                print "thats not a defense"
                continue

            for file in files:
                #avoid recalculating the original files
                if ("Tokyo" in file) or ("Fukushima" in file) or ("original" in file):  # do not load the original files, only the defenses (which are named after the defense)
                    print "Skipping", file, keyword
                    continue

                # case where not rounded as we can create clusters
                if (".csv"  in file) and ('avg' not in file ) and ('interpolated' not in file) \
                        and ('bak' not in file)  and (keyword != 0) \
                        and (keyword not in existinglist)  and (keyword in defs):
                    print root
                    print '-------------------',file
                    print keyword

                    dictd.clear()
                    df = pd.read_csv(os.path.join(root, file))  #read the file
                    if 'rounded' not in file:
                        savedict(df, keyword, starttime, endtime, minpoints, maxdistance, maxpois, 0,original_users)
                    elif ('rounded' in file) and ('4' in file):
                        savedict(df, keyword, starttime, endtime, minpoints, maxdistance, maxpois, 0,original_users)
                    else:
                        keyword = "rounded_" + str(params[0]) + "_digits"
                        savedict(df, keyword, starttime, endtime, minpoints, maxdistance, maxpois, 1,original_users)
                    names.append(keyword+str(params))
                else:
                    print "Skipping", file, keyword
        return 0



    #############################
    # function that manages the saving part of the privacy loss
    # decides on what to perform based on the keyword provided
    #

    def savedict(dfmain, keyword, starttime, endtime, minpoints, maxdistance, maxpois, rounded,original_users):

        df = preprocess(dfmain)  # preprocess the file, depending on the preferences one has in the init file

        if 'original' in keyword:
            original_users = df['User ID'].unique().tolist()  # get unique users who have clusters
            #print 'i am the original file'
            print original_users

        if not rounded :
            print('starting dict users for original')
            dictclusters(df, minpoints, maxdistance, maxpois, keyword, original_users)
            with open(DATA_BASE_WRITE_UTILITY + keyword + '.pickle', 'wb') as handle:
                #pickle.dump(dict(dictd), handle)
                pickle.dump(dictd, handle)
        else:
            print 'ok, going good'
            cluster_rounded(df, original_users, keyword)

            with open(DATA_BASE_WRITE_UTILITY + keyword + '.pickle', 'wb') as handle:
                #pickle.dump(dict(dictd), handle)
                pickle.dump(dictd, handle)

        return


    def dictclusters(df, minpoints, maxdistance, maxpois, keyword, original_users):
        dfgrouped = df.groupby(['User ID'])
        mylist = []
        for name, group in dfgrouped:
            if name in original_users:
                mylist.append((name,group))
                clusterfunc((name, group), minpoints, maxdistance, maxpois, keyword)

        #packedargs  =  partial(clusterfunc, minpoints=minpoints,
        #                       maxdistance = maxdistance,
        #                       maxpois=maxpois,
        #                       keyword = keyword)
        #callWorkers( packedargs, mylist )
        #myQueue.empty()
        return

    def callWorkers( packedargs, mylist):

        num_fetch_threads = 3
        printmsg("Working on {} threads".format(num_fetch_threads))
        pool = multiprocessing.Pool(processes=num_fetch_threads)
        result_list = pool.map(packedargs, mylist)
        pool.close()
        pool.join()
        #with ProcessPool(max_workers=1) as pool:
        #   future = pool.map(packedargs, mylist, timeout=9000)
        #   iterator = future.result()
        #   print('when i reture')
        #   while True:
        #       try:
        #           result = next(iterator)
        #       except StopIteration:
        #           break
        #       except TimeoutError as error:
        #           print("function took longer than %d seconds" % error.args[1])
        #       except ProcessExpired as error:
        #           print("%s. Exit code: %d" % (error, error.exitcode))
        #       except Exception as error:
        #           print("function raised %s" % error)
        #           print(error.message)  # Python's traceback of remote process

        printmsg( '#########################################   Done   ###########################################################')
        return 0

    def clusterfunc(item, minpoints, maxdistance, maxpois, keyword):
        name = item[0]
        group = item[1]
        printmsg( "{} on item {}".format(multiprocessing.current_process(), name))
        num_clusters = 0
        num_of_tries = 0
        nodesnum= 0
        tmp_max_distance = maxdistance
        tmp_min_points = minpoints
        spotsorigwgs84 = []
        tmptags = []
        nodeids = []

        lat = group.Latitude.values
        lon = group.Longitude.values
        datetimes = pd.to_datetime(group['Captured Time'].values)
        coords = np.array(list(zip(lat, lon)))  # get a list with all coordinatess
        coords_with_date = np.array(list(zip(lat, lon, datetimes)))

        if len(coords) == 0:
            print "No coords found!"
            return

        if 'original' in keyword:
            clusters_with_date, num_clusters = attackscript(tmp_min_points, tmp_max_distance, maxpois, coords,coords_with_date)

        elif advanced_clustering:
            clusters_with_date, num_clusters = attackscript(tmp_min_points, tmp_max_distance, maxpois, coords,coords_with_date)
        else:
            clusters_with_date, num_clusters = attackscript(tmp_min_points, tmp_max_distance, maxpois, coords,coords_with_date)

        #if you fail to create clusters maybe just let it go
        if num_clusters == 0:
            printmsg('Cant make clusters for this user: {}'.format(name))
            return

        for idx, cluster in enumerate(clusters_with_date):
            #parse coordinates
            fulldates = zip(*cluster)[2]
            dates = [j.date() for j in fulldates]
            distdates = len(set(dates))
            diff = ((max(fulldates) - min(fulldates)).total_seconds())/60.
            if distdates == 1 and diff< 30:
                printmsg('''Cant create cluster for user {} as he has {} distdates with {} minutes'''.format(name, distdates, diff))
                continue

            xorig = cluster[:, 0]
            yorig = cluster[:, 1]
            lonsorig, latsorig = pyproj.transform(wgs84, osm3857, yorig, xorig)
            xyorigwgs84 = zip(latsorig, lonsorig)
            pointsorigwgs84 = [Point(a, b) for a, b in xyorigwgs84]
            #draw a buffer around each point
            spotsorigwgs84.append([p.buffer(tmp_max_distance) for p in pointsorigwgs84])
            # flat out spots
        if len(spotsorigwgs84) == 0: return
        listorigwgs84 = []
        for i in spotsorigwgs84:
            for j in i:
                listorigwgs84.append(j)
        multiorigwgs84 = cascaded_union(listorigwgs84)
        multiorigwgs84 = multiorigwgs84.buffer(0)
        #print type(multiorigwgs84)

        if "MultiPolygon"  not in str(type(multiorigwgs84)):
            # plot polygon
            extorig = multiorigwgs84.exterior.xy
            lons, lats = pyproj.transform(osm3857, wgs84, extorig[1], extorig[0])
            # query osm
            c = zip(lats, lons)
            textquery = string_format(c)
            result= querypoly(textquery)
            try:
                if result != 0:
                    for j in result.nodes:
                        tmptags.append(j.tags)
                    nodeids.append(result.node_ids)
                    nodesnum = result.nodes.__len__()
            except ValueError:
                pass
        else:
            for i in multiorigwgs84:
                extorig = i.exterior.xy
                lons, lats = pyproj.transform(osm3857, wgs84, extorig[1], extorig[0])
                # query osm
                c = zip(lats, lons)
                textquery = string_format(c)
                result = querypoly(textquery)
                try:
                    if result !=0:
                        for j in result.nodes:
                            tmptags.append(j.tags)
                        nodeids.append(result.node_ids)
                        nodesnum += result.nodes.__len__()
                except ValueError:
                    pass

        atomic_operation(multiorigwgs84, name, tmptags, nodesnum, nodeids)
        return

    def adaptive_clustering_params(keyword, iteration, minpoints, maxdistance):
        if 'geoind' in keyword or 'remap' in keyword:
            return minpoints, maxdistance+10
        elif 'rnd_sample' in keyword:
            return minpoints-10, maxdistance
        elif 'spacex' in keyword:
            if minpoints >= min_allowed_points:return minpoints-10, maxdistance
            elif maxdistance<=max_allowed_distance: return minpoints, maxdistance+10
            else: print "something wrong with spacex"
        elif 'rounded' in keyword:
            return minpoints-10, maxdistance
        else:
            print '''something wrong with keywords and min/max points/distace'''


    ###############
    # Function to query to osm server for information
    # returns information inside a provided polygon
    #
    def querypoly(textquery):
        tries = 1
        while tries < 15:
            try:
                result =  api.query("""[timeout:1500][maxsize:2147483648];node(poly:"{}")["amenity" ~ ".+"];out skel;""".format(textquery))
                return result
            except overpy.exception.OverPyException as e:
                printmsg("{}  Caught exception when querying for poly. This was the {} try".format(multiprocessing.current_process(), tries))
                print e
                if "Timeout" in e:
                    tries += 2
                else:
                    tries +=1

            slp = random.randint(tries*1, tries*2)
            printmsg("Sleeping for {} seconds".format(slp))
            time.sleep(slp)
        return 0


    ###################################
    #Query the osm server for information withing a certain distance from a point
    #
    #
    #
    def queryaround(radius, lat, lon):
        tries=1
        while tries < 15:
            try:
                #printmsg("""Query looks like this,[timeout : 120];node(around:{},{},{})["amenity" ~ ".+"];out;""".format(radius, lat, lon) )
                result = api.query("""[timeout:1500][maxsize:2147483648];node(around:{},{},{})["amenity" ~ ".+"];out skel;""".format(radius, lat, lon))
                return result
            except overpy.exception.OverPyException as e:
                printmsg("{}  Caught exception when querying for around. This was the {} try".format(multiprocessing.current_process(), tries))
                print e
                if "Timeout" in e:
                    tries += 2
                else:
                    tries += 1

            slp = random.randint(tries*1, tries*2)
            printmsg("Sleeping for {} seconds".format(slp))
            time.sleep(slp)
        return 0



    ############################
    #
    # Convert the osm query to text
    # Its required for querying the server
    def string_format(l):
        string = ""
        cnt=1
        for i in l:
            if cnt ==1:
                string = string + "{} {}".format(repr(round(i[0], 4)),repr(round(i[1], 4)))
            else:
                string = string + " {} {}".format(repr(round(i[0], 4)), repr(round(i[1], 4)))
            cnt+=1
        return string

    def radiuspois(name, radius):
        tmptags = []
        #print radius
        lat = float(name[0])
        lon = float(name[1])
        if str(lat)[::-1].find('.')>5  or str(lon)[::-1].find('.')>5:
            print (lat,lon)
        nodesnum=0
        nodeids = []
        lonswgs84, latswgs84 = pyproj.transform(wgs84, osm3857, lon, lat)
        p = Point(latswgs84, lonswgs84)
        p = p.buffer(radius)
        poly = Polygon(p.exterior)

        result = queryaround(radius, lat, lon)
        if result != 0 and result.nodes!=[]:
            for j in result.nodes:
                tmptags.append(j.tags)
            nodeids.append(result.node_ids)
            nodesnum += result.nodes.__len__()
        atomic_operation(poly, str((lat,lon)), tmptags, nodesnum, nodeids)
        return  0

    def ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return

    def printmsg(text):
        with mylockprint:
            print text
        return

    def atomic_operation(multipolygon, name, tags, poislen,nodeids):
        dictd[name] = {"Polygon": multipolygon, "Nodes": tags, "Num_of_nodes": poislen, "Node_Ids": nodeids}
        #print dictd.keys()
            #print "returning"
        return dictd

    def existingfiles():
        tmp = []
        for root, dirs, files in os.walk(DATA_BASE_WRITE_UTILITY):
            for singlefile in files:
                main, ext = os.path.splitext(singlefile)

                tmp.append(main)
        print tmp
        return tmp

    def deletefiles(string, param):
        for root, dirs, files in os.walk(DATA_BASE_WRITE_UTILITY):
            for singlefile in files:
                main, ext = os.path.splitext(singlefile)
                if  ((string in main) and (param in main)):
                    print 'I will delete', singlefile
                    os.remove(os.path.join(root,singlefile))
                    print 'done'

        return 0

    def cluster_rounded(df, original_users,keyword):
        rounddigits = 0

        if '3' in keyword:
            rounddigits = 3
        elif '2' in keyword:
            rounddigits = 2
        else:
            printmsg("wrong radius from keyword, exiting")
            exit(-1)
        dfgrouped = df.groupby(['User ID'])
        mylist = []
        for name, group in dfgrouped:
            tmptags = []
            nodeids = []
            this_user_multipolygon = []
            this_user_multipolygon_3857 = []
            coords = []
            nodesnum = 0

            print name
            group = group.groupby(['Latitude', 'Longitude']).size().reindex().sort_values().tail(maxpois)

            for i in group.iteritems():
                tmp_points = return_square_verticres((i[0][0], i[0][1]), rounddigits )
                this_user_multipolygon.append(Polygon(tmp_points))
                xorig = []
                yorig = []

                for point in tmp_points:
                    xorig.append(point[0])
                    yorig.append(point[1])

                lonsorig, latsorig = pyproj.transform(wgs84, osm3857, yorig, xorig)
                coords_3857 = zip(latsorig, lonsorig)
                this_user_multipolygon_3857.append(Polygon(coords_3857))

            this_user_multipolygon_wgs84 = MultiPolygon(this_user_multipolygon)
            this_user_multipolygon_wgs84 = this_user_multipolygon_wgs84.buffer(0)

            this_user_multipolygon_3857 = MultiPolygon(this_user_multipolygon_3857)
            this_user_multipolygon_3857 = this_user_multipolygon_3857.buffer(0)

            if "MultiPolygon" not in str(type(this_user_multipolygon_wgs84)):
                    # plot polygon
                    extorig = this_user_multipolygon_wgs84.exterior.xy
                    lats = extorig[0]
                    lons = extorig[1]
                    # query osm
                    c = zip(lats, lons)
                    textquery = string_format(c)
                    result = querypoly(textquery)
                    try:
                        if result != 0:
                            for j in result.nodes:
                                tmptags.append(j.tags)
                            nodeids.append(result.node_ids)
                            nodesnum = result.nodes.__len__()
                    except ValueError:
                        pass
            else:
                    for i in this_user_multipolygon_wgs84:
                        extorig = i.exterior.xy
                        lats = extorig[0]
                        lons = extorig[1]

                        c = zip(lats, lons)
                        textquery = string_format(c)
                        result = querypoly(textquery)
                        print textquery
                        print '\n'
                        try:
                            if result != 0:
                                for j in result.nodes:
                                    tmptags.append(j.tags)
                                nodeids.append(result.node_ids)
                                nodesnum += result.nodes.__len__()
                        except ValueError:
                            pass
            atomic_operation(this_user_multipolygon_3857, name, tmptags, nodesnum, nodeids)

    def return_square_verticres(center, round_digits):
        if round_digits == 2:
            half_side = 0.005
        elif round_digits == 3:
            half_side =0.0005
        else:
            print 'wrong digits'
            exit()
        x = center[1]
        y = center[0]
        p2 = (y-half_side,x+half_side)
        p3 = (y+half_side, x+half_side)
        p1 = (y-half_side, x-half_side)
        p4 = ( y+half_side, x-half_side)
        #print p1,p2,p3,p4
        return  p1,p2,p3,p4

    mainprivacyloss(arg)


if __name__ == "__main__":
        pass