import privacy_gain
import plot_privacy_gain

from apply_defenses import *
from multiprocessing import  freeze_support
from plot_utilities import *
from __init__ import dataset_used
# the main automation function
# runs the defenses and
# calculates privacy loss


def runpipeline():
    
    # extract region and apply defenses
    apply_mechanisms(1) # apply defenses
    
    # Calculate users' privacy before and after defenses
    privacy_gain.main_privacy_gain(1) # ca lculate privacy loss

    # Calculate utility loss
    if 'Safecast' == dataset_used:
        safecast_utility()
    elif 'Radiocells' == dataset_used:
        radiocells_utility()
    else:
        pass


    # Calculate privacy gains and plot them
    plot_privacy_gain.create_colormap()
    plot_privacy_gain.parseuserdefs()
    plot_privacy_gain.plotscatter()
    return 0


if __name__ == "__main__":
    runpipeline()
