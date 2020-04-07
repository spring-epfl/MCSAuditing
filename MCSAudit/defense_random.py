"""
Defense mechanism where a part of the data is randomly deleted.
"""

import random

from .defense import AbstractDefense

class DefenseRandom(AbstractDefense):
    """
    Defense mechanism where a part of the points are randomly deleted.
    """

    def __init__(self, percentage, rng=None):

        # percentage bound to [0, 100]
        percentage = min(100, max(percentage, 0))
        self.percentage = percentage

        # By default, use Python's standard PRNG.
        if rng is None:
            self.rng = random.Random()
        self.rng = rng

        super().__init__()


    def compute(self, gps_points):

        gps_points.sort_values(['User ID', 'Captured Time'], inplace=True)

        # Randomly delete a percentage of the data.
        num_rows = len(gps_points.index)
        num_rows_delete = int(num_rows * (1 - self.percentage * 0.01))
        rows_delete = self.rng.sample(range(num_rows), num_rows_delete)
        rows_delete.sort()

        gps_points.drop(rows_delete)
