"""
Abstract dataset classes.
"""

from abc import ABC, abstractmethod

from pandas import array


class AbstractDataSet(ABC):
    """
    Dataset to use for teh simulation
    """

    dataset: array


    @abstractmethod
    def precompute(self):
        """
        Do some computations on the data set before using it in the simulation.
        """
