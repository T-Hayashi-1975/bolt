"""Tests for the pixel-to-meter conversion math."""

from __future__ import annotations

import math

import pytest

from haichizu.geo import (
    haversine_m,
    meters_per_pixel,
    pixel_distance_m,
    polygon_dimensions_m,
    within_2km,
)
from haichizu.models import ImageMetadata, Point


def test_meters_per_pixel_at_equator_zoom_0():
    # At zoom 0, the entire 256px tile spans the equator (≈40,075km)
    mpp = meters_per_pixel(0.0, zoom=0, scale=1)
    assert math.isclose(mpp * 256, 40_075_016.686, rel_tol=1e-6)


def test_meters_per_pixel_decreases_with_zoom():
    a = meters_per_pixel(35.0, zoom=18)
    b = meters_per_pixel(35.0, zoom=20)
    assert a / b == pytest.approx(4.0, rel=1e-9)


def test_meters_per_pixel_scale_2_halves_resolution():
    a = meters_per_pixel(35.0, zoom=20, scale=1)
    b = meters_per_pixel(35.0, zoom=20, scale=2)
    assert a / b == pytest.approx(2.0)


def test_pixel_distance_uses_metadata_scale():
    meta = ImageMetadata(
        center_lat=35.0,
        center_lng=137.0,
        zoom=20,
        width_px=1280,
        height_px=1280,
        scale=2,
    )
    p1 = Point(x=0, y=0)
    p2 = Point(x=100, y=0)
    expected = 100 * meters_per_pixel(35.0, 20, 2)
    assert pixel_distance_m(p1, p2, meta) == pytest.approx(expected)


def test_polygon_dimensions_returns_long_short():
    meta = ImageMetadata(
        center_lat=35.0, center_lng=137.0, zoom=20, width_px=1280, height_px=1280, scale=2
    )
    poly = [Point(x=0, y=0), Point(x=80, y=0), Point(x=80, y=200), Point(x=0, y=200)]
    longest, shortest = polygon_dimensions_m(poly, meta)
    assert longest > shortest
    assert longest == pytest.approx(200 * meters_per_pixel(35.0, 20, 2))
    assert shortest == pytest.approx(80 * meters_per_pixel(35.0, 20, 2))


def test_haversine_returns_zero_for_same_point():
    assert haversine_m(35.0, 137.0, 35.0, 137.0) == pytest.approx(0.0)


def test_within_2km_boundary():
    # ~1.85km north → within
    assert within_2km(35.0, 137.0, 35.0166, 137.0)
    # ~3.7km north → outside
    assert not within_2km(35.0, 137.0, 35.0333, 137.0)
