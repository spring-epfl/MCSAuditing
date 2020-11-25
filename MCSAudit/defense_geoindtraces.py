"""
Defense mechanism where some noise is added to the points.
"""

from random import Random

from cHaversine import haversine
from numpy import array

from .defense_lap_simple import DefenseLapSimple
from .logging import LOGGER


class DefenseGeoIndTraces(DefenseLapSimple):
    """
    Defense mechanism where some noise is added to the points.
    """

    def __init__(
            self,
            lmbda: float,
            radius: float,
            distance: float,
            rng: Random = None
        ) -> None:
        self.distance = distance

        super().__init__(lmbda, radius, rng)


    def __str__(self) -> str:
        """
        String representation.
        """
        return f"Geoind(e={self.epsilon}, d={self.distance})"


    def compute(self, gps_points: array) -> None:
        LOGGER.info("Compute %s", str(self))

        gps_points.sort_values(['User ID', 'Captured Time'], inplace=True)

        last_uid = None
        last_lat = None
        last_lon = None
        lat_mangled = None
        lon_mangled = None

        for _, row in gps_points.iterrows():
            lat, lon = DefenseGeoIndTraces.get_coords(row)

            if row['User ID'] != last_uid:
                last_uid = row['User ID']
                lat_mangled, lon_mangled = self.mangle_location(row)
                last_lat, last_lon = lat, lon

            # last_lat and last_lon must be set at this point.
            elif haversine((last_lat, last_lon), (lat, lon)) > self.distance:
                lat_mangled, lon_mangled = self.mangle_location(row)
                last_lat, last_lon = lat, lon

            else:
                DefenseGeoIndTraces.set_coords(row, lat_mangled, lon_mangled)
