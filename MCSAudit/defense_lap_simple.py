"""
Defense mechanism where some noise is added to the location of each point.
"""

from random import Random
from math import asin, atan2, cos, degrees, e, log, pi, radians, sin

from scipy.special import lambertw

from .defense import AbstractDefense


class DefenseLapSimple(AbstractDefense):
    """
    Defense mechanism where some noise is added to the location of each point.
    """

    earth_mean_radius = 6371.0088
    earth_mean_radius_inv = 1 / earth_mean_radius

    def __init__(self, lmbda, radius, rounding=5, rng=None):
        self.epsilon = log(lmbda) / radius
        self.rounding = rounding

        if rng is None:
            rng = Random(None)
        self.rng = rng

        super().__init__()


    def compute(self, gps_points):
        for _, row in gps_points.iterrows():
            self.mangle_location(row)
            DefenseLapSimple.round_coords(row, self.rounding)


    @staticmethod
    def get_coords(row):
        """Retrieve the coordinates from a row."""
        lat = row['Latitude']
        lon = row['Longitude']
        return lat, lon


    @staticmethod
    def set_coords(row, lat, lon):
        """Set the coordinates of a row."""
        row['Latitude'] = lat
        row['Longitude'] = lon


    @staticmethod
    def round_coords(row, num_decimal):
        """Round the coordinatess of a row"""
        lat, lon = DefenseLapSimple.get_coords(row)
        lat = round(lat, num_decimal)
        lon = round(lon, num_decimal)
        DefenseLapSimple.set_coords(row, lat, lon)


    def mangle_location(self, row):
        """Add noise to the point location."""
        lat, lon = DefenseLapSimple.get_coords(row)
        lat, lon = self.add_noise_to_coords(lat, lon)
        DefenseLapSimple.set_coords(row, lat, lon)
        return lat, lon


    def add_noise_to_coords(self, lat, lon):
        """Add noise to coordinates."""
        dist, angle = self.gen_noise()

        # Algorithm taken from legacy code, with cosmetic adaptations.
        # Original function: defense_mechanisms.addVectorToPos(pos, distance, angle)
        angular_dist = dist * DefenseLapSimple.earth_mean_radius_inv
        lat1 = radians(lat)
        lon1 = radians(lon)

        lat2 = asin(sin(lat1) * cos(angular_dist) + cos(lat1) * sin(angular_dist) * cos(angle))
        lon2 = lon1 + atan2(
            sin(angle) * sin(angular_dist) * cos(lat1),
            cos(angular_dist) - sin(lat1) * sin(lat2)
        )

        # normalise to [-pi, pi]
        lon2 = (lon2 + 3 * pi) % (2 * pi) - pi

        lat_deg = degrees(lat2)
        lon_deg = degrees(lon2)

        return lat_deg, lon_deg


    def gen_noise(self):
        """Generate some noise."""

        # Algorithm taken from legacy code, with cosmetic adaptations.
        # Original function: defense_mechanisms.compute_noise(param)
        angle = self.rng.uniform(0, 2 * pi)
        lambert = lambertw(-self.rng.uniform(0, 1 / e), k=-1)
        distance = -1 / self.epsilon * (lambert.real + 1)
        return distance, angle
