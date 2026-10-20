"""Haversine distance helpers (no PostGIS required)."""
from decimal import Decimal
from math import radians, sin, cos, asin, sqrt


EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometres between two WGS84 points."""
    if None in (lat1, lon1, lat2, lon2):
        return None
    lat1, lon1, lat2, lon2 = map(lambda v: radians(float(v)), (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * asin(sqrt(a))


def as_decimal_km(value):
    if value is None:
        return None
    return Decimal(str(round(value, 3)))
