import privacy_gain

from apply_defenses import *
from multiprocessing import  freeze_support
from plot_utilities import *
from __init__ import dataset_used
# the main automation function
# runs the defenses and
# calculates privacy loss


def runpipeline():
    #apply_mechanisms(1) # apply defenses
    privacy_gain.main_privacy_gain(1) # ca lculate privacy loss

    if 'Safecast' == dataset_used:
        safecast_utility()
    elif 'Radiocells' == dataset_used:
        radiocells_utility()
    else:
        pass

    return 0


if __name__ == "__main__":
    runpipeline()
