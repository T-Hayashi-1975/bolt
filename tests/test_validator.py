"""Tests for the legal/practical rule engine."""

from __future__ import annotations

from haichizu.models import (
    AnalysisResult,
    ApplicantInfo,
    ImageMetadata,
    ParkingSpace,
    Point,
)
from haichizu.validator import validate

META = ImageMetadata(
    center_lat=35.0,
    center_lng=137.0,
    zoom=20,
    width_px=1280,
    height_px=1280,
    scale=2,
)


def _space(space_id: str, w_px: int, h_px: int) -> ParkingSpace:
    return ParkingSpace(
        id=space_id,
        polygon=[
            Point(x=0, y=0),
            Point(x=w_px, y=0),
            Point(x=w_px, y=h_px),
            Point(x=0, y=h_px),
        ],
    )


def _applicant(target_id: str, length_cm: int = 480, width_cm: int = 180) -> ApplicantInfo:
    return ApplicantInfo(
        applicant_name="テスト",
        vehicle_make="トヨタ",
        vehicle_model_code="ZSU60W",
        vehicle_length_cm=length_cm,
        vehicle_width_cm=width_cm,
        target_space_id=target_id,
    )


def test_missing_target_space_emits_error():
    analysis = AnalysisResult(spaces=[_space("A", 80, 200)], entrances=[], roads=[])
    issues = validate(analysis, _applicant("Z"), META)
    codes = [i.code for i in issues]
    assert "target_space_missing" in codes
    assert any(i.severity == "error" for i in issues)


def test_undersized_space_flagged():
    # 20×30 px at zoom=20 scale=2 (~0.062 m/px) ≈ 1.25m × 1.88m — too small for any vehicle
    analysis = AnalysisResult(spaces=[_space("A", 20, 30)], entrances=[], roads=[])
    issues = validate(analysis, _applicant("A"), META)
    codes = {i.code for i in issues}
    assert {"space_too_short", "space_too_narrow"}.issubset(codes)


def test_no_entrance_or_road_emits_warnings():
    analysis = AnalysisResult(spaces=[_space("A", 80, 200)], entrances=[], roads=[])
    issues = validate(analysis, _applicant("A"), META)
    codes = {i.code for i in issues}
    assert "entrance_not_detected" in codes
    assert "road_not_detected" in codes


def test_disclaimer_always_present():
    analysis = AnalysisResult(spaces=[_space("A", 80, 200)], entrances=[], roads=[])
    issues = validate(analysis, _applicant("A"), META)
    assert any(i.code == "ai_draft_disclaimer" for i in issues)
