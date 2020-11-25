"""
Defense mechanism
"""

import math
from math import cos, sin
from pathlib import Path
from random import Random
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from numpy import array

from scipy.spatial import cKDTree
from scipy.special import lambertw
from shapely.geometry import Point, Polygon
from sklearn.metrics.pairwise import pairwise_distances

from .constants import (
    KEY_LAT,
    KEY_LON
)
from .defense_lap_simple import DefenseLapSimple
from .logging import LOGGER

class PostCoordsError(Exception):
    """An error occured while computing the posterior coordinates."""

class NoPriorDataComputed(Exception):
    """No prior data was precomputed."""


class DefenseLapRemapped(DefenseLapSimple):
    """
    Defense mechanism where some noise is added to the location of each point.
    """

    prior_coords_x = None # type: array
    coords_x = None # type: array
    kd_tree = None # type: array

    def __init__(
            self,
            lmbda: float,
            radius: float,
            rounding: int = 5,
            p_norm: float = 2.0,
            tolerance: float = 1.0e-9,
            rng: Optional[Random] = None,
        ) -> None:
        self.p_norm = p_norm
        self.tolerance = tolerance

        # Called here to init `self.epsilon`.
        super().__init__(lmbda, radius, rounding, rng)

        lambert = lambertw(0.01 / math.e, k=-1).real + 1

        self.radius = -lambert / self.epsilon


    def __str__(self) -> str:
        """
        String representation
        """
        return f"Lap remapped(e={self.epsilon}, r={self.radius})"


    def compute(self, gps_points: array) -> None:
        LOGGER.info("Compute %s", str(self))

        if (
                DefenseLapRemapped.prior_coords_x is None or
                DefenseLapRemapped.coords_x is None or
                DefenseLapRemapped.kd_tree is None
            ):
            raise NoPriorDataComputed()

        for _, row in gps_points.iterrows():
            self.mangle_location(row)
            coords = DefenseLapRemapped.to_cartesian(row)
            coords_np = np.array(coords)
            indices = DefenseLapRemapped.kd_tree.query_ball_point(
                coords_np, p=self.p_norm, r=self.radius
            )

            if indices:
                # pylint: disable=unsubscriptable-object
                coords = DefenseLapRemapped.coords_x[indices]
                distances = pairwise_distances([coords_np], coords)
                post_coords = self.compute_post_coords(distances, indices)
                loc_opt = DefenseLapRemapped.compute_geometric_median(
                    post_coords[:], coords
                )
                lat, lon = loc_opt[0], loc_opt[1]

                if not (np.isnan(lat) or np.isnan(lon)):
                    DefenseLapSimple.set_coords(row, lat, lon)

            DefenseLapSimple.round_coords(row, self.rounding)


    @staticmethod
    def extract_region_from_world(
            coords_csv_in: Path,
            region_polygon: Optional[Polygon] = None,
            is_whole_world: bool = True
        ) -> pd.DataFrame:
        """
        Exctract the points in a region defined by a polygon.
        """

        # If the region is whole world, the polygon should be None.
        if (
                (region_polygon is None and not is_whole_world) or
                (region_polygon is not None and is_whole_world)
            ):
            raise ValueError()

        in_region = list()

        for chunk in pd.read_csv(coords_csv_in, iterator=True, chunksize=1_000_000):

            chunk_in_region = chunk.dropna(axis=0, subset=["offset"])

            if not is_whole_world:
                in_region_indexes = chunk_in_region.apply(
                    lambda row: Point(row[KEY_LAT], row[KEY_LON]).within(
                        region_polygon
                    ),
                    axis=1,
                )
                chunk_in_region = chunk[in_region_indexes]

            in_region.append(chunk_in_region)

        region = pd.concat(in_region, ignore_index=True)

        return region


    @classmethod
    def precompute(
            cls,
            locations: array,
            rounding: int = 3,
            leafsize: int = 4000
        ) -> None:
        """
        Compute prior coordinates.
        """
        LOGGER.info("Precompute locations for DefenseLapRemapped")

        locations[KEY_LAT] = locations[KEY_LAT].apply(
            lambda x: round(x, rounding)
        )
        locations[KEY_LON] = locations[KEY_LON].apply(
            lambda x: round(x, rounding)
        )
        coords = (
            locations.groupby([KEY_LAT, KEY_LON])
            .size()
            .reset_index()
            .rename(columns={0: "PriorX"})
        )

        # Normalize
        prior_x_sum = coords["PriorX"].sum()
        coords["PriorX"] = coords["PriorX"] / prior_x_sum
        coords = coords.drop_duplicates()

        # coords_x = np.loadtxt(priors_transformed_path, skiprows=1, usecols=(0, 1), delimiter=",")
        coords_x = coords[:, 0:2]

        cartesian_coords = np.asarray(
            list(DefenseLapRemapped.to_cartesian(angles) for angles in coords_x)
        )

        kd_tree = cKDTree(cartesian_coords, leafsize=leafsize)

        # prior_x = np.loadtxt(priors_transformed_path, skiprows=1, usecols=(2,), delimiter=",")
        prior_x = coords[:, 2:3]

        # Same data but in different structure.
        prior_x.shape = (prior_x.shape[0], 1)

        cls.prior_coords_x = prior_x
        cls.coords_x = coords_x
        cls.kd_tree = kd_tree


    def compute_post_coords(
            self,
            distances: array,
            indices
        ) -> array:
        """Compute posterior coordinates."""
        arr_shape = distances[0].shape
        dist = np.vstack((distances[0], np.zeros(shape=arr_shape)))
        factor = np.exp(-self.epsilon * dist.transpose())

        # pylint: disable=unsubscriptable-object
        post_coords = DefenseLapRemapped.prior_coords_x[indices] * factor
        post_coords_sum = np.sum(post_coords[:, 1])
        post_coords = np.multiply(DefenseLapRemapped.prior_coords_x[indices], factor)

        post_coords = np.divide(post_coords[:, 1], post_coords_sum)

        if abs(np.sum(post_coords) - 1) > self.tolerance:
            raise PostCoordsError

        return post_coords


    @staticmethod
    def to_cartesian(row: array) -> Tuple[float, float]:
        """Convert angular coordinates to cartesian ones."""
        lat, lon = DefenseLapRemapped.get_coords(row)
        lat = math.radians(lat)
        lon = math.radians(lon)

        coord_x = DefenseLapRemapped.earth_mean_radius * cos(lat) * cos(lon)
        coord_y = DefenseLapRemapped.earth_mean_radius * cos(lat) * sin(lon)

        return (coord_x, coord_y)


    @staticmethod
    def compute_geometric_median(
            probabilities_in: array,
            values_in: array,
            tolerance: float = 1.0e-3,
            max_iterations: float = 200
        ):
        """Computes the geometric median."""
        # Weiszfeld's algorithm
        probabilities = np.copy(probabilities_in)
        values = np.copy(values_in)

        probabilities = probabilities[probabilities > 0]  # remove zero entries
        values = values[probabilities]  # remove entries of values with probability of 0

        geo_median_old = np.array((math.inf, math.inf))
        geo_median = np.dot(
            probabilities.transpose(), values
        )  # Initial estimation is the mean

        iter_max = max_iterations

        while np.linalg.norm(geo_median, geo_median_old) > tolerance and iter_max > 0:

            distance_matrix = pairwise_distances([geo_median], values)[0]

            # Return if there is a zero value in distance_matrix
            if np.any(distance_matrix == 0):
                return geo_median

            geo_median_old = geo_median
            div = np.divide(probabilities, distance_matrix)
            geo_median = np.divide(
                np.dot(div, values), np.dot(div, np.ones_like(values))
            )
            iter_max -= 1

        return geo_median
