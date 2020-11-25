"""
Defense mechanism where some noise is added to the location of each point.
"""

from math import asin, atan2, cos, degrees, e, log, pi, radians, sin
from random import Random
from typing import Tuple

from numpy import array
from scipy.special import lambertw

from .constants import (
    KEY_LAT,
    KEY_LON
)
from .defense import AbstractDefense
from .logging import LOGGER

class DefenseLapSimple(AbstractDefense):
    """
    Defense mechanism where some noise is added to the location of each point.
    """

    earth_mean_radius = 6371.0088
    earth_mean_radius_inv = 1 / earth_mean_radius

    def __init__(
            self,
            lmbda: float,
            radius: float,
            rounding: int = 5,
            rng: Random = None
        ) -> None:
        self.epsilon = log(lmbda) / radius
        self.rounding = rounding

        if rng is None:
            rng = Random(None)
        self.rng = rng

        super().__init__()


    def __str__(self) -> str:
        """
        String representation
        """
        return f"Lap simple(e={self.epsilon})"


    def compute(self, gps_points: array) -> None:
        LOGGER.info("Compute %s", str(self))

        for _, row in gps_points.iterrows():
            self.mangle_location(row)
            DefenseLapSimple.round_coords(row, self.rounding)


    @staticmethod
    def get_coords(row: array) -> Tuple:
        """
        Retrieve the coordinates from a row.
        """

        lat = row[KEY_LAT]
        lon = row[KEY_LON]
        return lat, lon


    @staticmethod
    def set_coords(row, lat: float, lon: float) -> None:
        """
        Set the coordinates of a row.
        """

        row[KEY_LAT] = lat
        row[KEY_LON] = lon


    @staticmethod
    def round_coords(row, num_decimal: int) -> None:
        """Round the coordinatess of a row"""
        lat, lon = DefenseLapSimple.get_coords(row)
        lat = round(lat, num_decimal)
        lon = round(lon, num_decimal)
        DefenseLapSimple.set_coords(row, lat, lon)


    def mangle_location(self, row: array) -> Tuple[float, float]:
        """Add noise to the point location."""
        lat, lon = DefenseLapSimple.get_coords(row)
        lat, lon = self.add_noise_to_coords(lat, lon)
        DefenseLapSimple.set_coords(row, lat, lon)
        return lat, lon


    def add_noise_to_coords(self, lat: float, lon: float) -> Tuple[float, float]:
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


    def gen_noise(self) -> Tuple[float, float]:
        """Generate some noise."""

        # Algorithm taken from legacy code, with cosmetic adaptations.
        # Original function: defense_mechanisms.compute_noise(param)
        angle = self.rng.uniform(0, 2 * pi)
        lambert = lambertw(-self.rng.uniform(0, 1 / e), k=-1)
        distance = -1 / self.epsilon * (lambert.real + 1)
        return distance, angle
