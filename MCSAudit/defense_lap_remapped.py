"""
Defense mechanism
"""

import math
from math import cos, e, radians, sin

import numpy as np

from scipy.special import lambertw
from sklearn.metrics.pairwise import pairwise_distances

from .defense_lap_simple import DefenseLapSimple


class PostCoordsError(Exception):
    """An error occured while computing the posterior coordinates."""


class DefenseLapRemapped(DefenseLapSimple):
    """
    Defense mechanism where some noise is added to the location of each point.
    """

    def __init__(self, lmbda, radius, prior_coords, coords, kdtree, rounding=5, p_norm=2.0, tolerance=1.0e-9, rng=None):
        self.prior_coords = prior_coords
        self.coords = coords
        self.kdtree = kdtree
        self.p_norm = p_norm
        self.tolerance = tolerance

        # Called here to init `self.epsilon`.
        super().__init__(lmbda, radius, rounding, rng)

        lambert = lambertw(0.01 / e, k=-1).real + 1

        self.radius = -lambert / self.epsilon


    def compute(self, gps_points):
        for _, row in gps_points.iterrows():
            self.mangle_location(row)
            coords = DefenseLapRemapped.to_cartesian(row)
            coords_np = np.array(coords)
            indices = self.kdtree.query_ball_point(coords_np, p=self.p_norm, r=self.radius)

            if indices:
                coords = self.coords[indices]
                distances = pairwise_distances([coords_np], coords)
                post_coords = self.compute_post_coords(distances, indices)
                loc_opt = DefenseLapRemapped.compute_geometric_median(post_coords[:], coords)
                lat, lon = loc_opt[0], loc_opt[1]

                if not (np.isnan(lat) or np.isnan(lon)):
                    DefenseLapSimple.set_coords(row, lat, lon)

            DefenseLapSimple.round_coords(row, self.rounding)


    def compute_prior_coords(self):
        """
        Compute prior coordinates
        """


    def compute_post_coords(self, distances, indices):
        """Compute posterior coordinates."""
        arr_shape = distances[0].shape
        dist = np.vstack((distances[0], np.zeros(shape=arr_shape)))
        factor = np.exp(-self.epsilon * dist.transpose())

        post_coords = self.prior_coords[indices] * factor
        post_coords_sum = np.sum(post_coords[:, 1])
        post_coords = np.multiply(self.prior_coords[indices], factor)

        post_coords = np.divide(post_coords[:, 1], post_coords_sum)

        if abs(np.sum(post_coords) - 1) > self.tolerance:
            raise PostCoordsError

        return post_coords


    @staticmethod
    def to_cartesian(row):
        """Convert angular coordinates to cartesian ones."""
        lat, lon = DefenseLapRemapped.get_coords(row)
        lat = radians(lat)
        lon = radians(lon)

        coord_x = DefenseLapRemapped.earth_mean_radius * cos(lat) * cos(lon)
        coord_y = DefenseLapRemapped.earth_mean_radius * cos(lat) * sin(lon)

        return (coord_x, coord_y)


    @staticmethod
    def compute_geometric_median(probabilities_in, values_in, tolerance=1.0e-3, max_iterations=200):
        """Computes the geometric median."""
        # Weiszfeld's algorithm
        probabilities = np.copy(probabilities_in)
        values = np.copy(values_in)

        probabilities = probabilities[probabilities > 0]  # remove zero entries
        values = values[probabilities]  # remove entries of values with probability of 0

        geo_median_old = np.array((math.inf, math.inf))
        geo_median = np.dot(probabilities.transpose(), values)  # Initial estimation is the mean

        iter_max = max_iterations

        while np.linalg.norm(geo_median, geo_median_old) > tolerance and iter_max > 0:

            distance_matrix = pairwise_distances([geo_median], values)[0]

            # Return if there is a zero value in distance_matrix
            if np.any(distance_matrix == 0):
                return geo_median

            geo_median_old = geo_median
            div = np.divide(probabilities, distance_matrix)
            geo_median = np.divide(np.dot(div, values), np.dot(div, np.ones_like(values)))
            iter_max -= 1

        return geo_median
