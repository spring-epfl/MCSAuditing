import pandas as pd
import cPickle as pickle
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from pylab import plot, show, savefig, xlim, figure,  hold, ylim, legend, boxplot, setp, axes
from matplotlib.lines import Line2D
from __init__ import (starttime, endtime, place,minpoints, maxdistance,
                      writeplace, DATA_BASE_WRITE_UTILITY,defenses_path,original_pickle,advanced_clustering, mypath,
                      datapath_to_original_file, privacyloss_path,utilities_plot,
                      return_write_path)


plt.rc('font', family='serif', serif='Times')
plt.rc('text', usetex=True)
SMALL_SIZE = 9
MEDIUM_SIZE = 11
BIGGER_SIZE = 11

plt.rc('font', size=MEDIUM_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)  # legend fontsize
plt.rc('figure', titlesize=MEDIUM_SIZE)  # fontsize of the figure title
rotation = 45
width = 8.2
height = 6
flierprops = dict(marker='.', markerfacecolor='k', markersize=2,
                      linestyle='none', markeredgecolor='k')


def parseuserdefs():
    # load up original meas and inter
    cities=['World']

    savename='cities'
    if advanced_clustering:
        savename = savename+'advanced'
    else:
        savename = savename+'standard'
    cities_dict = {}
    defs = ['geoind[1.6, 0.05]',
            'geoind[1.6, 0.15]',
            'geoind[1.6, 0.3]',
            'remap[1.6, 0.05]',
            'remap[1.6, 0.15]',
            'remap[1.6, 0.3]',
            'rnd_sample[40]',
            'rnd_sample[60]',
            'rnd_sample[80]',
            'rounded_2_digits',
            'rounded_3_digits',
            'rounded[4]',
            'geoind_traces[1.6, 0.05, 30.0]',
            'geoind_traces[1.6, 0.05, 60.0]',
            'geoind_traces[1.6, 0.05, 90.0]',
            'spacex[30.0]',
            'spacex[60.0]',
            'spacex[90.0]']

    new_name_defs = ['GeoInd: 50m',
                     'GeoInd: 150m',
                     'GeoInd: 300m',
                     'GeoInd-OR: 50m',
                     'GeoInd-OR: 150m',
                     'GeoInd-OR: 300m',
                     'Random: 40%',
                     'Random: 60%',
                     'Random: 80%',
                     'Rounding: 2',
                     'Rounding: 3',
                     'Rounding: 4',
                     'Release-GeoInd: 30m',
                     'Release-GeoInd: 60m',
                     'Release-GeoInd: 90m',
                     'Release: 30m',
                     'Release: 60m',
                     'Release: 90m']

    print 'original pickle loaded'

    for citynum, city in enumerate(cities):
        cities_dict[city] = {}
        thisplace = city
        writeplace = return_write_path(city)

        print '''I will read from {}'''.format(writeplace)
        # place = 'Tokyobak'
        DATA_PATH = privacyloss_path + writeplace + "/"
        print DATA_PATH
        original_file_toread = datapath_to_original_file
        dfmain = pd.read_csv(original_file_toread)
        print 'original file read'

        df = dfmain[((pd.to_datetime(dfmain['Captured Time']) + (
                    pd.to_timedelta(dfmain['offset'] / 60, unit='h'))).dt.hour > starttime) &
                            ((pd.to_datetime(dfmain['Captured Time']) + (
                            pd.to_timedelta(dfmain['offset'] / 60, unit='h'))).dt.hour < endtime) &
                            ((pd.to_datetime(dfmain['Captured Time']) + (
                            pd.to_timedelta(dfmain['offset'] / 60, unit='h'))).dt.dayofweek < 5)]

        print 'hours changed and parsed'

        with open(original_pickle, "rb+") as f:
            doriginal = pickle.load(f)

        listorig = doriginal.keys()
        a = set(listorig)

        for defidx,item in enumerate(defs):
            print defidx, item
            cities_dict[city][new_name_defs[defidx]]={}
            cities_dict[city][new_name_defs[defidx]]['topusers'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers'] = {}

            cities_dict[city][new_name_defs[defidx]]['topusers']['clusters'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers']['clusters'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers']['clusters'] = {}

            cities_dict[city][new_name_defs[defidx]]['topusers']['pois'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers']['pois'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers']['pois'] = {}

            cities_dict[city][new_name_defs[defidx]]['topusers']['clusters']['precision'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers']['clusters']['precision'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers']['clusters']['precision'] = {}
            cities_dict[city][new_name_defs[defidx]]['topusers']['clusters']['recall'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers']['clusters']['recall'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers']['clusters']['recall'] = {}

            cities_dict[city][new_name_defs[defidx]]['topusers']['pois']['precision'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers']['pois']['precision'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers']['pois']['precision'] = {}
            cities_dict[city][new_name_defs[defidx]]['topusers']['pois']['recall'] = {}
            cities_dict[city][new_name_defs[defidx]]['medusers']['pois']['recall'] = {}
            cities_dict[city][new_name_defs[defidx]]['lowusers']['pois']['recall'] = {}

            try:
                with open(os.path.join(DATA_PATH, item + '.pickle'), "rb+") as f:
                    dfake = pickle.load(f)
            except IOError as e:
                print e
                continue

            listfake = dfake.keys()
            b = set(listfake)
            c = list(a.intersection(b))

            topusers = []
            medusers = []
            lowusers = []
            topuserspois = []
            meduserspois = []
            lowuserspois = []
            fdrlist_pois = []
            recall_list_pois = []
            precisionlist_pois = []

            if c:
                for idx, i in enumerate(c):
                    counts = len(df[df['User ID'] == i].index)

                    try:

                        intersection = (doriginal[i]['Polygon'].intersection(dfake[i]['Polygon'])).area
                        fdr = ( dfake[i]['Polygon'].area - intersection ) / dfake[i]['Polygon'].area
                        precision = 1-fdr
                        recall = intersection / doriginal[i]['Polygon'].area

                        if counts > 50000:
                            topusers.append((precision, recall))
                        elif counts > 10000:
                            medusers.append((precision, recall))
                        else:
                            lowusers.append((precision, recall))

                    except ZeroDivisionError:
                        pass

                    poisb4 = doriginal[i]['Node_Ids']
                    poisb4 = [elem for elem in poisb4 if elem != []]
                    poisb4 = [j for elem in poisb4 for j in elem]
                    poisafter = dfake[i]['Node_Ids']
                    poisafter = [elem for elem in poisafter if elem != []]
                    poisafter = [j for elem in poisafter for j in elem]
                    try:
                        poisb4 = [j for elem in poisb4 for j in elem]
                    except TypeError:
                        pass
                    try:
                        poisafter = [j for elem in poisafter for j in elem]
                    except TypeError:
                        pass

                    try:

                        tp_pois = float(len(set(poisb4) - (set(poisb4) - set(poisafter))))
                        fdr_pois = (float(len(poisafter)) - tp_pois) / len(poisafter)
                        precision_pois = 1 - fdr_pois
                        recall_pois = tp_pois / len(poisb4)
                        if counts > 50000:
                            topuserspois.append((precision_pois, recall_pois))
                        elif counts > 10000:
                            meduserspois.append((precision_pois, recall_pois))
                        else:
                            lowuserspois.append((precision_pois, recall_pois))

                    except ZeroDivisionError:
                        pass

                try:
                    cities_dict[city][new_name_defs[defidx]]['topusers']['clusters']['precision'] = zip(*topusers)[0]
                    cities_dict[city][new_name_defs[defidx]]['topusers']['clusters']['recall'] = zip(*topusers)[1]

                except IndexError as err:
                    pass
                try:
                    cities_dict[city][new_name_defs[defidx]]['medusers']['clusters']['precision'] = zip(*medusers)[0]
                    cities_dict[city][new_name_defs[defidx]]['medusers']['clusters']['recall'] = zip(*medusers)[1]

                except IndexError as err:
                    pass

                try:
                    cities_dict[city][new_name_defs[defidx]]['lowusers']['clusters']['precision'] = zip(*lowusers)[0]
                    cities_dict[city][new_name_defs[defidx]]['lowusers']['clusters']['recall'] = zip(*lowusers)[1]

                except IndexError as err:
                    pass



                try:
                    cities_dict[city][new_name_defs[defidx]]['topusers']['pois']['precision'] = zip(*topuserspois)[0]
                    cities_dict[city][new_name_defs[defidx]]['topusers']['pois']['recall'] = zip(*topuserspois)[1]

                except IndexError as err:
                    pass
                try:
                    cities_dict[city][new_name_defs[defidx]]['medusers']['pois']['precision'] = zip(*meduserspois)[0]
                    cities_dict[city][new_name_defs[defidx]]['medusers']['pois']['recall'] = zip(*meduserspois)[1]

                except IndexError as err:
                    pass

                try:
                    cities_dict[city][new_name_defs[defidx]]['lowusers']['pois']['precision'] = zip(*lowuserspois)[0]
                    cities_dict[city][new_name_defs[defidx]]['lowusers']['pois']['recall'] = zip(*lowuserspois)[1]

                except IndexError as err:
                    pass

    with open(privacyloss_path+"clustersimgafinal{}.pickle".format(savename),"wb+")as f:
        pickle.dump(cities_dict,f)


def plotscatter():
    cities = ['World']
    myfigure, axes = plt.subplots(2, 3, sharey='all', figsize=(width, height))
    disc_dict = {}
    savename='cities'
    if advanced_clustering:
        savename = savename+'advanced'
    else:
        savename = savename+'standard'

    defs = ['GeoInd: 50m',
            'GeoInd: 150m',
            'GeoInd: 300m',
            'GeoInd-OR: 50m',
            'GeoInd-OR: 150m',
            'GeoInd-OR: 300m',
            'Random: 40%',
            'Random: 60%',
            'Random: 80%',
            'Rounding: 2',
            'Rounding: 3',
            'Rounding: 4',
            'Release-GeoInd: 30m',
            'Release-GeoInd: 60m',
            'Release-GeoInd: 90m',
            'Release: 30m',
            'Release: 60m',
            'Release: 90m']

    with open(mypath + "cm.pickle", "rb+") as f:
        cmap = pickle.load(f)
    print 'colors loaded'
    legend_elements = []
    legendpois_elements = []
    for defidx, item in enumerate(defs):
        legend_elements.append(Line2D([0], [0], color=cmap[item], label=defs[defidx]))

    legendpois_elements = [Line2D([], [], linestyle='None', marker='^', color='k', label='$x > 50K$'),
                       Line2D([], [], linestyle='None', marker='o', color='k', label='$10K < x < 50K$'),
                       Line2D([], [], linestyle='None', marker='+', color='k', label='$x < 10K$')]

    with open(privacyloss_path+"clustersimgafinal{}.pickle".format(savename), "rb") as mypickleplot:
        d = pickle.load(mypickleplot)
    print 'image file read'

    for citynum ,city in enumerate(cities):
        print city
        disc_dict[city] = {}

        if 'Tokyo' in city:
            total = 30
        elif 'Fukushima' in city:
            total = 104
        else:
            total = 537

        disc_dict[city]['total'] = total

        for defense in d[city].keys():

            if not 'GeoInd' in defense: pass
            print "------------",defense
            try:
                axes[0,citynum].scatter(list(d[city][defense]['topusers']['clusters']['precision']),
                                      list(d[city][defense]['topusers']['clusters']['recall']), c=cmap[defense], s=26, marker="^")
            except KeyError as err:
                print err

            try:
                axes[0, citynum].scatter(list(d[city][defense]['medusers']['clusters']['precision']),
                                          list(d[city][defense]['medusers']['clusters']['recall']), c=cmap[defense], s=26, marker="o")
            except KeyError as err:
                print err

            try:
                axes[0, citynum].scatter(list(d[city][defense]['lowusers']['clusters']['precision']),
                                          list(d[city][defense]['lowusers']['clusters']['recall']), c=cmap[defense], s=26, marker="+")
            except KeyError as err:
                print err

            disc_dict[city][defense] = disc_dict[city]['total'] - (len(d[city][defense]['lowusers']['clusters']['precision']) +
                                                                   len(d[city][defense]['medusers']['clusters']['precision']) +
                                                                   len(d[city][defense]['topusers']['clusters']['precision']) )

        axes[0,citynum].spines["top"].set_visible(False)
        axes[0,citynum].spines["bottom"].set_visible(True)
        axes[0,citynum].spines["right"].set_visible(False)
        axes[0,citynum].spines["left"].set_visible(True)
        axes[0,citynum].set(xlim=[-0.1, 1.1],
                              ylim=[-0.1, 1.1],
                              aspect=1,
                              xticks  = [0,0.25,0.5,0.75,1])

    for citynum, city in enumerate(cities):
        print city

        for defense in d[city].keys():

            print "------------",defense
            try:
                axes[1, citynum].scatter(list(d[city][defense]['topusers']['pois']['precision']),
                                          list(d[city][defense]['topusers']['pois']['recall']), c=cmap[defense],
                                          s=26, marker="^")
            except KeyError as err:
                print err

            try:
                axes[1, citynum].scatter(list(d[city][defense]['medusers']['pois']['precision']),
                                          list(d[city][defense]['medusers']['pois']['recall']), c=cmap[defense],
                                          s=26, marker="o")
            except KeyError as err:
                print err

            try:
                axes[1, citynum].scatter(list(d[city][defense]['lowusers']['pois']['precision']),
                                          list(d[city][defense]['lowusers']['pois']['recall']), c=cmap[defense],
                                          s=26, marker="+")
            except KeyError as err:
                print err

        axes[1,citynum].spines["top"].set_visible(False)
        axes[1,citynum].spines["bottom"].set_visible(True)
        axes[1,citynum].spines["right"].set_visible(False)
        axes[1,citynum].spines["left"].set_visible(True)
        axes[1,citynum].set(xlim=[-0.1, 1.1],
                              ylim=[-0.1, 1.1],
                              aspect=1,
                              xticks=[0, 0.25, 0.5, 0.75, 1])

    mylegend = plt.figlegend(bbox_to_anchor=(0.5, 0.97), loc='upper center', ncol=6, labelspacing=0.,
                             handles=legend_elements, title='Defenses', prop={'size': 9})
    myfigure.text(0.5, 0.04, 'Precision', ha='center')
    myfigure.text(0.06, 0.5, 'Recall', va='center', rotation='vertical')

    myfigure.text(0.035, 0.3, 'POIs', va='center', rotation='vertical')
    myfigure.text(0.035, 0.7, 'Spatial', va='center', rotation='vertical')

    myfigure.text(0.235, 0.469, 'Tokyo', ha='center')
    myfigure.text(0.517, 0.469, 'Fukushima', ha='center')
    myfigure.text(0.785, 0.469, 'World', ha='center')

    #mylegend2 = plt.figlegend(bbox_to_anchor=(0.5, 0.89), loc='upper center', labelspacing=0.,
                              #handles=legendpois_elements, title='Amount of Measurements (x)', ncol=3)
    leg_lines = mylegend.get_lines()
    plt.setp(leg_lines, linewidth=3)
    mylegend.get_frame().set_alpha(0)
    mylegend.get_frame().set_edgecolor('white')

    plt.savefig(utilities_plot+'privacy_gain_{}.png'.format(savename),dpi=360, transparent =True, frameon= False,bbox_inches='tight')

    #plt.show()
    for i in disc_dict.keys():
        print i
        for j in  disc_dict[i].keys():
            print j, ":", disc_dict[i][j]


def create_colormap():
    new_colors = {'GeoInd-OR: 50m': 'orange',
                  'GeoInd-OR: 150m': 'coral',
                  'GeoInd-OR: 300m': 'red',
                  'GeoInd: 50m': 'silver',
                  'GeoInd: 150m': 'gray',
                  'GeoInd: 300m': 'k',
                  'Random: 40%': 'lightgreen',
                  'Random: 60%': 'yellowgreen',
                  'Random: 80%': 'g',
                  'Release: 60m': 'aqua',
                  'Release: 90m': 'b',
                  'Release: 30m': 'skyblue',
                  'Rounding: 2': 'violet',
                  'Rounding: 3': 'fuchsia',
                  'Rounding: 4': 'deeppink',
                  'Release-GeoInd: 30m':'yellow',
                  'Release-GeoInd: 60m':'y',
                  'Release-GeoInd: 90m':'olive'}

    with open(mypath+"cm.pickle", "wb+") as f:
        pickle.dump(new_colors,f)


if __name__ == "__main__":
    create_colormap()
    parseuserdefs()
    plotscatter()
