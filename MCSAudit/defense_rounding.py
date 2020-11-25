"""
Defense mechanism by rounding the numbers to an arbitrary precision.
"""

from numpy import array

from .defense import AbstractDefense
from .constants import (
    KEY_LAT,
    KEY_LON
)
from .logging import LOGGER


class DefenseRounding(AbstractDefense):
    """
    Defense mechanism by rounding the numbers to an arbitrary precision.
    """

    def __init__(self, digits: int) -> None:
        self.digits = digits
        super().__init__()


    def __str__(self) -> str:
        """
        String representation
        """
        return f"Rounding(n={self.digits})"


    def compute(self, gps_points: array) -> None:
        LOGGER.info("Compute %s", str(self))

        # Do a simple rounding.
        pd_params = {
            KEY_LAT: self.digits,
            KEY_LON: self.digits
        }
        gps_points.round(pd_params)
