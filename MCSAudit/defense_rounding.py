"""
Defense mechanism by rounding the numbers to an arbitrary precision.
"""

from .defense import AbstractDefense

class DefenseRounding(AbstractDefense):
    """
    Defense mechanism by rounding the numbers to an arbitrary precision.
    """

    def __init__(self, num_digits):
        self.num_digits = num_digits
        super().__init__()


    def compute(self, gps_points):

        # Do a simple rounding.
        pd_params = {
            'Latitude': self.num_digits,
            'Longitude': self.num_digits
        }
        gps_points.round(pd_params)
