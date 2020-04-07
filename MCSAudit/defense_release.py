"""
Defense mechanism where the points are kept only if they are at a minimal
distance one from an other.
"""

import pandas as pd

from cHaversine import haversine

from .defense import AbstractDefense

class DefenseRelease(AbstractDefense):
    """
    Defense mechanism where the points are kept only if they are at a minimal
    distance one from an other.
    """

    def __init__(self, radius):
        self.radius = radius


    def compute(self, gps_points):
        gps_points.sort_values('Captured Time', inplace=True)
        grouped = gps_points.groupby('User ID')

        for _, points_by_uid in grouped:
            places = list(zip(points_by_uid.Latitude.values, points_by_uid.Longitude.values))
            datetimes = pd.to_datetime(points_by_uid['Captured Time'].values)
            indexes = points_by_uid.index()

            rows_delete = list()

            # The first element is always kept.
            indexes.pop(0)
            last = (places.pop(0), datetimes.pop(0))

            # Remove points within minimal distance of the previous one taken in the same day.
            for index, place, datetime in zip(indexes, places, datetimes):
                if haversine(last[0], place) > self.radius or last[1].date() != datetime.date():
                    # Keep that point. Compare the next points to that one.
                    last = (place, datetime)
                else:
                    rows_delete.append(index)

            # delete the rows that needs to be deleted if needed.
            if rows_delete:
                rows_delete.sort()
                gps_points.drop(rows_delete)
