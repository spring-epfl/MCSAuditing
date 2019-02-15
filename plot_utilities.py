import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from cHaversine import haversine
from __init__ import defenses_path, place, filespath, DATA_PATH, utilities_plot
from apply_defenses import ensure_dir


def safecast_utility():
    ensure_dir(utilities_plot)

    plt.rc('font', family='serif', serif='Times')
    plt.rc('text', usetex=True)
    SMALL_SIZE = 9
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 11

    plt.rc('font', size=MEDIUM_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=MEDIUM_SIZE)  # fontsize of the figure title
    flierprops = dict(marker='+', markerfacecolor='r', markersize=0.3,
                      linestyle='none', markeredgecolor='r')

    boxprops = dict(linestyle='--')
    medianprops = dict(linestyle='-', linewidth=2.5, color='k')

    rotation = 45
    width = 4.5
    height = 3.5
    defs = ['geoind_lamda_1.6_radius_0.05_method_lap',
            'geoind_lamda_1.6_radius_0.15_method_lap',
            'geoind_lamda_1.6_radius_0.3_method_lap',
            'geoind_lamda_1.6_radius_0.05_method_lap_remapping',
            'geoind_lamda_1.6_radius_0.15_method_lap_remapping',
            'geoind_lamda_1.6_radius_0.3_method_lap_remapping',
            'geoind_traces_1.6_radius_0.05_distance_30',
            'geoind_traces_1.6_radius_0.05_distance_60',
            'geoind_traces_1.6_radius_0.05_distance_90',
            'random_sample_80_percent',
            'random_sample_60_percent',
            'random_sample_40_percent',
            'rounded_4_digits',
            'rounded_3_digits',
            'rounded_2_digits',
            'spacex_30_meters',
            'spacex_60_meters',
            'spacex_90_meters']

    new_name_defs = ['GeoInd: 50m',
                     'GeoInd: 150m',
                     'GeoInd: 300m',
                     'GeoInd-OR: 50m',
                     'GeoInd-OR: 150m',
                     'GeoInd-OR: 300m',
                     'Release-GeoInd: 30m',
                     'Release-GeoInd: 60m',
                     'Release-GeoInd: 90m',
                     'Random: 80%',
                     'Random: 60%',
                     'Random: 40%',
                     'Rounding: 4',
                     'Rounding: 3',
                     'Rounding: 2',
                     'Release: 30m',
                     'Release: 60m',
                     'Release: 90m']

    data_to_plot = []
    data_to_plot_ushv = []
    data_to_plot_mape = []
    names = []
    vals = []
    origpath = defenses_path + '/{}/'.format(place)+place+'.interpolated.csv'
    orig = pd.read_csv(origpath, header = None)
    oricat = orig.values.ravel()
    oricat = (oricat/350.0)*8.760
    oricat = np.array(oricat.tolist())

    dfs= []
    allparams = []
    plotpure = []
    plotpure.append(orig.values.ravel())
    namestmp = []
    namestmp.append('original')
    categorical = []
    for defidx,item in enumerate(defs):
        try:
            df = pd.read_csv(defenses_path + '/{}/{}.interpolated.csv'.format(item, item),header = None)
        except IOError as e:
            print e
            continue
        plotpure.append((df.values.ravel()).round(3))
        ss = df.subtract(orig)
        defcat = ss.values.ravel()
        defcat = (defcat/350.0)*8.760 # safecast radiation transformation
        defcat = np.array(defcat.tolist())
        ss = ss.abs()
        ss = ss.values
        ss = ss.ravel()
        data_to_plot.append(np.round(ss, decimals=2))
        data_to_plot_ushv.append((ss/350.0).round(3))
        tt = orig.subtract(df)
        tt = tt.div(orig)
        tt = tt.abs()
        tt = tt*100
        tt =tt.values
        tt = tt.ravel()
        data_to_plot_mape.append(tt.round(3))
        names.append(new_name_defs[defidx])
        namestmp.append(new_name_defs[defidx])
        vals.append(np.count_nonzero(~np.isnan(ss)))

    ##### difference
    fig1 = plt.figure(1,figsize=(width,height))

    # Create an axes instance
    ax1 = fig1.gca()

    # Create the boxplot
    bp1 = ax1.boxplot(data_to_plot,flierprops=flierprops,boxprops=boxprops, medianprops=medianprops,
                      widths = 0.35, patch_artist=False, showmeans = False)#, boxprops=dict(facecolor="lightblue"))

    ax1.set_xticklabels(names,  rotation=rotation, ha='right', minor=False)
    ax1.spines["top"].set_visible(False)
    ax1.spines["bottom"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)

    ax1.set_yscale('symlog', linthreshy=10)
    minax,maxax = ax1.set_ylim(10 ** -6, 10 ** 5)

    ax1.set_ylabel('cpm')

    fig1.tight_layout()

    plt.savefig(utilities_plot +place+'Absolute_Difference.png',dpi=360, transparent =True, frameon= False)


def radiocells_utility():
    ensure_dir(utilities_plot)

    plt.rc('font', family='serif', serif='Times')
    plt.rc('text', usetex=True)
    flierprops = dict(marker='+', markerfacecolor='r', markersize=0.3,
                      linestyle='none', markeredgecolor='r')

    boxprops = dict(linestyle='--')
    medianprops = dict(linestyle='-', linewidth=2.5, color='k')
    SMALL_SIZE = 9
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 11
    plt.rc('font', size=MEDIUM_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=MEDIUM_SIZE)  # fontsize of the figure title
    rotation = 45
    width = 4.5
    height = 3.5

    defs = ['geoind_lamda_1.6_radius_0.05_method_lap',
            'geoind_lamda_1.6_radius_0.15_method_lap',
            'geoind_lamda_1.6_radius_0.3_method_lap',
            'geoind_lamda_1.6_radius_0.05_method_lap_remapping',
            'geoind_lamda_1.6_radius_0.15_method_lap_remapping',
            'geoind_lamda_1.6_radius_0.3_method_lap_remapping',
            'geoind_traces_1.6_radius_0.05_distance_30',
            'geoind_traces_1.6_radius_0.05_distance_60',
            'geoind_traces_1.6_radius_0.05_distance_90',
            'random_sample_80_percent',
            'random_sample_60_percent',
            'random_sample_40_percent',
            'rounded_4_digits',
            'rounded_3_digits',
            'rounded_2_digits',
            'spacex_30_meters',
            'spacex_60_meters',
            'spacex_90_meters']

    new_name_defs = ['GeoInd: 50m',
                     'GeoInd: 150m',
                     'GeoInd: 300m',
                     'GeoInd-OR: 50m',
                     'GeoInd-OR: 150m',
                     'GeoInd-OR: 300m',
                     'Release-GeoInd: 30m',
                     'Release-GeoInd: 60m',
                     'Release-GeoInd: 90m',
                     'Random: 80%',
                     'Random: 60%',
                     'Random: 40%',
                     'Rounding: 4',
                     'Rounding: 3',
                     'Rounding: 2',
                     'Release: 30m',
                     'Release: 60m',
                     'Release: 90m']


    cities = ['World']

    for city in cities:
        place = city
        origpath = defenses_path + place+'/{}.avg.csv'.format(place)
        thispath = defenses_path
        print 'reading {}'.format(origpath)
        dorig = pd.read_csv(origpath,dtype={'mcc': int, 'mnc': int})
        print dorig
        print defenses_path
        boxplots = []
        names=[]
        for defidx, item in enumerate(defs):
            try:
                ddef = pd.read_csv(thispath + '/{}/{}.avg.csv'.format(item, item),dtype={'mcc': int, 'mnc': int})
                print(ddef)

            except IOError as e:
                print e
                continue

            df = pd.merge(dorig, ddef, how='inner', on=['mcc', 'mnc', 'lac', 'Cellid'])
            tmp = []
            for row in df.itertuples():
                tmp.append(int(haversine((row[5], row[6]), (row[7], row[8]))))
            boxplots.append(tmp)
            names.append(new_name_defs[defidx])
            ##### difference
        fig5 = plt.figure(1, figsize=(width, height))
        # Create an axes instance
        ax5 = fig5.gca()

        # Create the boxplot
        bp = ax5.boxplot(boxplots, boxprops=boxprops,flierprops=flierprops, medianprops=medianprops,
                         widths=0.35, patch_artist=False)
        ax5.set_xticklabels(names, rotation=rotation, ha='right', minor=False)
        ax5.spines["top"].set_visible(False)
        ax5.spines["bottom"].set_visible(False)
        ax5.spines["right"].set_visible(False)
        ax5.spines["left"].set_visible(False)
        plt.title('Utility loss in Radiocells dataset'.format(city))
        plt.ylabel('Meters')
        plt.tight_layout()
        plt.savefig(utilities_plot + 'radiocells_utilityloss.png', dpi=360, transparent =False, frameon= False)
        #plt.show()
        plt.gcf().clear()
        fig5.gca().clear()
