"""Pixel-to-meter conversion using Google Static Maps' Web Mercator projection."""

from __future__ import annotations

import math

from haichizu.models import ImageMetadata, Point

EARTH_CIRCUMFERENCE_M = 40_075_016.686
TILE_SIZE = 256


def meters_per_pixel(lat_deg: float, zoom: int, scale: int = 1) -> float:
    """Ground resolution at the given latitude/zoom for Web Mercator tiles.

    Reference: https://developers.google.com/maps/documentation/javascript/coordinates
    Formula: 156543.03392 * cos(lat) / 2^zoom
    """
    if zoom < 0:
        raise ValueError("zoom must be non-negative")
    lat_rad = math.radians(lat_deg)
    base = EARTH_CIRCUMFERENCE_M * math.cos(lat_rad) / (TILE_SIZE * (2**zoom))
    return base / scale


def pixel_distance_m(p1: Point, p2: Point, meta: ImageMetadata) -> float:
    """Straight-line distance between two image points in meters."""
    mpp = meters_per_pixel(meta.center_lat, meta.zoom, meta.scale)
    dx = (p2.x - p1.x) * mpp
    dy = (p2.y - p1.y) * mpp
    return math.hypot(dx, dy)


def polygon_dimensions_m(polygon: list[Point], meta: ImageMetadata) -> tuple[float, float]:
    """Approximate (width, depth) of a parking-space polygon in meters.

    Uses the minimum-area bounding rectangle approach via the longest and
    shortest edges of the polygon (sufficient for axis-aligned parking spaces).
    """
    if len(polygon) < 3:
        raise ValueError("polygon must have at least 3 vertices")
    edges = [
        pixel_distance_m(polygon[i], polygon[(i + 1) % len(polygon)], meta)
        for i in range(len(polygon))
    ]
    longest = max(edges)
    shortest = min(e for e in edges if e > 0)
    return longest, shortest


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two coordinates in meters."""
    r = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def within_2km(home_lat: float, home_lng: float, lot_lat: float, lot_lng: float) -> bool:
    """車庫証明 requires home ↔ parking lot ≤ 2 km (straight line)."""
    return haversine_m(home_lat, home_lng, lot_lat, lot_lng) <= 2000.0
