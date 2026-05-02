"""Data models for the 配置図 pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Point(BaseModel):
    """Image-coordinate point in pixels (origin: top-left)."""

    x: float
    y: float


class ParkingSpace(BaseModel):
    """A single detected parking space."""

    id: str = Field(description="区画番号 (e.g. '1', 'A-3')")
    polygon: list[Point] = Field(
        description="Pixel polygon vertices, clockwise from top-left",
        min_length=3,
    )
    is_target: bool = Field(default=False, description="申請対象区画か")


class Entrance(BaseModel):
    """Entrance/exit between parking lot and road."""

    midpoint: Point
    width_px: float = Field(gt=0, description="Width in pixels")
    facing: Literal["north", "south", "east", "west"] | None = None


class Road(BaseModel):
    """Adjacent public road."""

    name: str | None = None
    side: Literal["north", "south", "east", "west"]
    width_m: float | None = Field(default=None, gt=0, description="Estimated width in meters")
    confidence: Literal["low", "medium", "high"] = "medium"


class AnalysisResult(BaseModel):
    """Output of the Claude Vision analysis stage."""

    spaces: list[ParkingSpace]
    entrances: list[Entrance]
    roads: list[Road]
    notes: str = Field(
        default="",
        description="Free-form caveats from the vision model (visibility, occlusion, etc.)",
    )
    detected_landmarks: list[str] = Field(
        default_factory=list,
        description="Building/landmark names visible in the image (e.g. 'chocoZAP豊田元町')",
    )


class ApplicantInfo(BaseModel):
    """Applicant-side metadata required on a 配置図."""

    applicant_name: str
    vehicle_make: str = Field(description="車名（メーカー名）")
    vehicle_model_code: str = Field(description="型式")
    vehicle_length_cm: int = Field(default=480, gt=0)
    vehicle_width_cm: int = Field(default=180, gt=0)
    target_space_id: str = Field(description="申請する区画ID")


class ImageMetadata(BaseModel):
    """Geographic metadata for an aerial image."""

    center_lat: float
    center_lng: float
    zoom: int = Field(ge=0, le=22)
    width_px: int = Field(gt=0)
    height_px: int = Field(gt=0)
    scale: int = Field(default=1, description="Static Maps API scale (1 or 2)")
    source: Literal["google_static", "gsi", "user_upload"] = "google_static"


class GenerationRequest(BaseModel):
    """Top-level request: combines image + analysis + applicant info."""

    image_path: str
    image_meta: ImageMetadata
    applicant: ApplicantInfo
    analysis: AnalysisResult
    output_path: str = "output/haichizu.svg"


class ValidationIssue(BaseModel):
    """A legal/practical issue flagged by the rule engine."""

    severity: Literal["error", "warning", "info"]
    code: str
    message: str
