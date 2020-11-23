"""
Abstract dataset classes.
"""

from abc import ABC, abstractmethod


class AbstractDataSet(ABC):
    """
    Dataset to use for teh simulation
    """

    @abstractmethod
    def precompute(self):
        """
        Do some computations on the data set before using it in the simulation.
        """
