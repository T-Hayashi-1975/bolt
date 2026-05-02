"""Rule engine for legal/practical validation of a 配置図 draft."""

from __future__ import annotations

from haichizu.geo import polygon_dimensions_m
from haichizu.models import (
    AnalysisResult,
    ApplicantInfo,
    ImageMetadata,
    ValidationIssue,
)


def validate(
    analysis: AnalysisResult,
    applicant: ApplicantInfo,
    meta: ImageMetadata,
) -> list[ValidationIssue]:
    """Run legal/practical checks against the analysis."""
    issues: list[ValidationIssue] = []

    target = next((s for s in analysis.spaces if s.id == applicant.target_space_id), None)
    if target is None:
        issues.append(
            ValidationIssue(
                severity="error",
                code="target_space_missing",
                message=f"申請対象区画 '{applicant.target_space_id}' が検出結果に存在しません。",
            )
        )
        return issues

    longest_m, shortest_m = polygon_dimensions_m(target.polygon, meta)
    vehicle_length_m = applicant.vehicle_length_cm / 100
    vehicle_width_m = applicant.vehicle_width_cm / 100

    if longest_m + 0.05 < vehicle_length_m:
        issues.append(
            ValidationIssue(
                severity="error",
                code="space_too_short",
                message=(
                    f"区画長 {longest_m:.2f}m が車長 {vehicle_length_m:.2f}m を下回ります。"
                ),
            )
        )
    if shortest_m + 0.05 < vehicle_width_m:
        issues.append(
            ValidationIssue(
                severity="error",
                code="space_too_narrow",
                message=(
                    f"区画幅 {shortest_m:.2f}m が車幅 {vehicle_width_m:.2f}m を下回ります。"
                ),
            )
        )

    if not analysis.entrances:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="entrance_not_detected",
                message="出入口が検出できませんでした。現地確認のうえ手動で記入してください。",
            )
        )
    if not analysis.roads:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="road_not_detected",
                message="接道道路が検出できませんでした。道路台帳と現地確認が必要です。",
            )
        )
    for road in analysis.roads:
        if road.width_m is None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="road_width_unknown",
                    message=f"{road.side}側道路の幅員が不明です。実測または道路台帳で補完してください。",
                )
            )

    issues.append(
        ValidationIssue(
            severity="info",
            code="ai_draft_disclaimer",
            message=(
                "本配置図はAIによる下書きです。寸法・方位・出入口・申請区画の特定は"
                "必ず現地実測のうえ行政書士が確認・補正してください。"
            ),
        )
    )
    return issues
