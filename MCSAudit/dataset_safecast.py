"""
Safecast data set
"""

import logging

from numpy import array
import numpy as np
from scipy.interpolate import griddata

from .constants import (
    KEY_CPM_MEAN,
    KEY_LAT,
    KEY_LAT_MEAN,
    KEY_LON,
    KEY_LON_MEAN,
    KEY_N,
    KEY_VAL
)
from .dataset import AbstractDataSet


class DataSetSafecast(AbstractDataSet):
    """
    Safecast data set
    """

    def __init__(
            self,
            dataset: array,
            gridsize: int = 1500,
            cpm_thresold: int = 20000,
            rounding: int = 6
        ) -> None:
        self.dataset = dataset
        self.gridsize = gridsize
        self.cpm_thresold = cpm_thresold
        self.rounding = rounding


    def precompute(self) -> None:
        dataset = self.compute_mean()

        lon_max = dataset[KEY_LON_MEAN].max()
        lat_min = dataset[KEY_LAT_MEAN].min()
        lat_max = dataset[KEY_LAT_MEAN].max()
        lon_min = dataset[KEY_LON_MEAN].min()

        # Filter out the points at the min/max latitude/longitude.
        dataset = dataset[(
            (dataset[:, KEY_LAT_MEAN] > lat_min) &
            (dataset[:, KEY_LAT_MEAN] < lat_max) &
            (dataset[:, KEY_LON_MEAN] > lon_min) &
            (dataset[:, KEY_LON_MEAN] < lon_max)
        )]

        # Extract coordinates
        coords = dataset[:, [KEY_LAT_MEAN, KEY_LON_MEAN]]
        cpms = dataset[:, KEY_CPM_MEAN]

        axis_lat = np.linspace(lat_min, lat_max, self.gridsize)
        axis_lon = np.linspace(lon_min, lon_max, self.gridsize)
        grid_lon, grid_lat = np.meshgrid(axis_lon, axis_lat)

        try:
            interpolation = griddata(coords, cpms, (grid_lon, grid_lat), method="nearest")
        except RuntimeError:
            logging.exception("Failed to interpolate the dataset.")

        grid = interpolation.reshape((self.gridsize, self.gridsize))

        self.dataset = grid


    def compute_mean(self) -> array:
        """
        Compute the mean values of the dataset.
        """
        dataset = np.copy(self.dataset)

        dataset[KEY_LAT] = dataset[KEY_LAT].apply(lambda lat: round(lat, self.rounding))
        dataset[KEY_LON] = dataset[KEY_LON].apply(lambda lon: round(lon, self.rounding))

        dataset = (
            dataset[[KEY_LAT, KEY_LON, KEY_VAL]]
            .groupby(by=[KEY_LAT, KEY_LON])
            .agg(["mean", "count"])
            .reset_index()
        )

        dataset.columns = [KEY_LAT_MEAN, KEY_LON_MEAN, KEY_CPM_MEAN, KEY_N]

        return dataset
