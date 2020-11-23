"""
Radio cells data set
"""

from numpy import array

from .constants import (
    KEY_CELL_ID,
    KEY_LAC,
    KEY_LAT,
    KEY_LON,
    KEY_MCC,
    KEY_MNC,
)
from .dataset import AbstractDataSet


class DataSetRadioCells(AbstractDataSet):
    """
    Radio cells data set
    """

    def __init__(self, dataset: array):
        self.dataset = dataset


    def precompute(self):
        self.dataset = (
            self.dataset
            .groupby([KEY_MCC, KEY_MNC, KEY_LAC, KEY_CELL_ID])[KEY_LAT, KEY_LON]
            .mean()
            .reset_index()
        )
