"""Attack classes."""

from abc import ABC, abstractmethod

class AbstractAttack(ABC):
    """Attack abstract class.
    To create a daughter class, define abstract method `compute()`.
    """

    def __init__(self, gps_points):
        """Default constructor
        Call the parser and store the data set.
        """

        # The data set is considered small enough to be held in memory.
        self.gps_points = self.parser(gps_points)


    def parser(self, gps_points):
        """Dummy parser.
        Override if needed.
        """
        return gps_points


    @abstractmethod
    def compute(self):
        """Compute the attack to apply to the data set."""
        pass