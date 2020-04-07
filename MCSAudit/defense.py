"""Defense classes."""

from abc import ABC, abstractmethod

import pandas as pd

class AbstractDefense(ABC):
    """Defense abstract class.
    To create a daughter class, define abstract method `compute()`.
    """

    @abstractmethod
    def compute(self, gps_points):
        """Compute the defenses to apply to the data set."""
