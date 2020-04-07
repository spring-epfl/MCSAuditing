"""
Defense mechanism where some noise is added to the points.
"""

from cHaversine import haversine

from .defense_lap_simple import DefenseLapSimple


class DefenseGeoIndTraces(DefenseLapSimple):
    """
    Defense mechanism where some noise is added to the points.
    """

    def __init__(self, lmbda, radius, distance, rng=None):
        self.distance = distance

        super().__init__(lmbda, radius, rng)


    def compute(self, gps_points):
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

            elif haversine((last_lat, last_lon), (lat, lon)) > self.distance:
                lat_mangled, lon_mangled = self.mangle_location(row)
                last_lat, last_lon = lat, lon

            else:
                DefenseGeoIndTraces.set_coords(row, lat_mangled, lon_mangled)
