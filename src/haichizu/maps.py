"""Thin wrapper for the Google Static Maps API."""

from __future__ import annotations

import os
from pathlib import Path

import requests

from haichizu.models import ImageMetadata

STATIC_MAPS_URL = "https://maps.googleapis.com/maps/api/staticmap"


def fetch_satellite(
    lat: float,
    lng: float,
    zoom: int,
    out_path: str | Path,
    *,
    size_px: tuple[int, int] = (640, 640),
    scale: int = 2,
    api_key: str | None = None,
) -> ImageMetadata:
    """Download a satellite tile and return its geographic metadata.

    The free tier allows up to 640×640 with scale=2 (effectively 1280×1280).
    """
    api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_MAPS_API_KEY not set. Pass --api-key or set the env var."
        )
    params = {
        "center": f"{lat},{lng}",
        "zoom": zoom,
        "size": f"{size_px[0]}x{size_px[1]}",
        "scale": scale,
        "maptype": "satellite",
        "format": "png",
        "key": api_key,
    }
    resp = requests.get(STATIC_MAPS_URL, params=params, timeout=30)
    resp.raise_for_status()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(resp.content)
    return ImageMetadata(
        center_lat=lat,
        center_lng=lng,
        zoom=zoom,
        width_px=size_px[0] * scale,
        height_px=size_px[1] * scale,
        scale=scale,
        source="google_static",
    )
