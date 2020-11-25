"""Defense classes."""

from abc import ABC, abstractmethod

from numpy import array


class AbstractDefense(ABC):
    """Defense abstract class.
    To create a daughter class, define abstract method `compute()`.
    """

    @abstractmethod
    def compute(self, gps_points: array) -> None:
        """Compute the defenses to apply to the data set."""
