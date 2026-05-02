"""SVG generation for the 配置図 (parking-lot configuration drawing).

Produces an A4-portrait SVG sized in millimeters. Conversion from image
pixels to drawing millimeters uses the satellite image's known meters/pixel
combined with a chosen drawing scale (default 1:100).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import svgwrite

from haichizu.geo import meters_per_pixel
from haichizu.models import (
    AnalysisResult,
    ApplicantInfo,
    ImageMetadata,
    ParkingSpace,
    Point,
    ValidationIssue,
)

A4_W_MM = 210
A4_H_MM = 297
MARGIN_MM = 10
DRAWING_SCALE = 100  # 1:100 — 1m on the ground = 10mm on paper


def _bbox(spaces: list[ParkingSpace]) -> tuple[float, float, float, float]:
    xs = [p.x for s in spaces for p in s.polygon]
    ys = [p.y for s in spaces for p in s.polygon]
    return min(xs), min(ys), max(xs), max(ys)


def _project(
    p: Point,
    bbox: tuple[float, float, float, float],
    mpp: float,
    offset_mm: tuple[float, float],
) -> tuple[float, float]:
    """Image-px → drawing-mm using fixed scale (1m → 10mm at 1:100)."""
    min_x, min_y, _, _ = bbox
    px_to_mm = mpp * 1000 / DRAWING_SCALE
    return (
        offset_mm[0] + (p.x - min_x) * px_to_mm,
        offset_mm[1] + (p.y - min_y) * px_to_mm,
    )


def _polygon_centroid(polygon: list[Point]) -> Point:
    n = len(polygon)
    return Point(x=sum(p.x for p in polygon) / n, y=sum(p.y for p in polygon) / n)


def _polygon_dims_m(polygon: list[Point], mpp: float) -> tuple[float, float]:
    edges = []
    for i in range(len(polygon)):
        a, b = polygon[i], polygon[(i + 1) % len(polygon)]
        edges.append(((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5 * mpp)
    return max(edges), min(e for e in edges if e > 0)


def render_svg(
    analysis: AnalysisResult,
    applicant: ApplicantInfo,
    meta: ImageMetadata,
    issues: list[ValidationIssue],
    out_path: str | Path,
) -> Path:
    """Render the analysis to an A4 SVG at 1:100 and return the output path."""
    if not analysis.spaces:
        raise ValueError("No parking spaces in analysis; cannot render 配置図")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    dwg = svgwrite.Drawing(str(out), size=(f"{A4_W_MM}mm", f"{A4_H_MM}mm"))
    dwg.viewbox(0, 0, A4_W_MM, A4_H_MM)

    dwg.add(
        dwg.rect(
            insert=(MARGIN_MM, MARGIN_MM),
            size=(A4_W_MM - 2 * MARGIN_MM, A4_H_MM - 2 * MARGIN_MM),
            stroke="black",
            stroke_width=0.4,
            fill="white",
        )
    )

    title = f"配置図（縮尺 1:{DRAWING_SCALE}）— {applicant.applicant_name}"
    dwg.add(
        dwg.text(
            title,
            insert=(MARGIN_MM + 2, MARGIN_MM + 6),
            font_size=4,
            font_family="sans-serif",
        )
    )

    mpp = meters_per_pixel(meta.center_lat, meta.zoom, meta.scale)
    bbox = _bbox(analysis.spaces)
    offset_mm = (MARGIN_MM + 5, MARGIN_MM + 15)

    for space in analysis.spaces:
        pts = [_project(p, bbox, mpp, offset_mm) for p in space.polygon]
        is_target = space.id == applicant.target_space_id or space.is_target
        dwg.add(
            dwg.polygon(
                points=pts,
                fill="#ffe0e0" if is_target else "white",
                stroke="red" if is_target else "black",
                stroke_width=0.6 if is_target else 0.3,
            )
        )
        cx, cy = _project(_polygon_centroid(space.polygon), bbox, mpp, offset_mm)
        dwg.add(
            dwg.text(
                space.id,
                insert=(cx, cy),
                font_size=2.5,
                text_anchor="middle",
                font_family="sans-serif",
                fill="red" if is_target else "black",
            )
        )

    target_space = next(
        (s for s in analysis.spaces if s.id == applicant.target_space_id),
        None,
    )
    if target_space is not None:
        long_m, short_m = _polygon_dims_m(target_space.polygon, mpp)
        cx, cy = _project(_polygon_centroid(target_space.polygon), bbox, mpp, offset_mm)
        dwg.add(
            dwg.text(
                f"申請区画 {short_m:.1f}m × {long_m:.1f}m",
                insert=(cx, cy + 4),
                font_size=2.0,
                text_anchor="middle",
                font_family="sans-serif",
                fill="red",
            )
        )

    arrow_x, arrow_y = A4_W_MM - MARGIN_MM - 12, MARGIN_MM + 18
    dwg.add(
        dwg.line(
            start=(arrow_x, arrow_y + 8),
            end=(arrow_x, arrow_y),
            stroke="black",
            stroke_width=0.5,
        )
    )
    dwg.add(
        dwg.polygon(
            points=[(arrow_x, arrow_y - 1), (arrow_x - 1.5, arrow_y + 2), (arrow_x + 1.5, arrow_y + 2)],
            fill="black",
        )
    )
    dwg.add(
        dwg.text(
            "N",
            insert=(arrow_x, arrow_y - 2),
            font_size=3,
            text_anchor="middle",
            font_family="sans-serif",
        )
    )

    legend_y = A4_H_MM - MARGIN_MM - 60
    legend_x = MARGIN_MM + 4
    dwg.add(
        dwg.text(
            "■ 凡例",
            insert=(legend_x, legend_y),
            font_size=3,
            font_family="sans-serif",
            font_weight="bold",
        )
    )
    legend_y += 4
    legend_lines = [
        f"申請者：{applicant.applicant_name}",
        f"車名／型式：{applicant.vehicle_make} / {applicant.vehicle_model_code}",
        f"車両寸法：長さ{applicant.vehicle_length_cm/100:.2f}m × 幅{applicant.vehicle_width_cm/100:.2f}m",
        f"画像中心：({meta.center_lat:.6f}, {meta.center_lng:.6f})  zoom={meta.zoom}",
        f"地理スケール：{mpp:.3f} m/px   作図縮尺：1/{DRAWING_SCALE}",
        f"出力日：{date.today().isoformat()}",
    ]
    for line in legend_lines:
        dwg.add(
            dwg.text(
                line,
                insert=(legend_x, legend_y),
                font_size=2.5,
                font_family="sans-serif",
            )
        )
        legend_y += 3

    if analysis.detected_landmarks:
        dwg.add(
            dwg.text(
                "周辺ランドマーク：" + " / ".join(analysis.detected_landmarks),
                insert=(legend_x, legend_y),
                font_size=2.5,
                font_family="sans-serif",
            )
        )
        legend_y += 3

    legend_y += 2
    dwg.add(
        dwg.text(
            "■ 検証結果",
            insert=(legend_x, legend_y),
            font_size=3,
            font_family="sans-serif",
            font_weight="bold",
        )
    )
    legend_y += 4
    if not issues:
        dwg.add(
            dwg.text(
                "（指摘事項なし）",
                insert=(legend_x, legend_y),
                font_size=2.5,
                font_family="sans-serif",
            )
        )
    else:
        for issue in issues:
            color = {"error": "red", "warning": "#cc7a00", "info": "black"}[issue.severity]
            dwg.add(
                dwg.text(
                    f"[{issue.severity.upper()}] {issue.message}",
                    insert=(legend_x, legend_y),
                    font_size=2.3,
                    font_family="sans-serif",
                    fill=color,
                )
            )
            legend_y += 2.8

    dwg.add(
        dwg.text(
            "※ 本図はAIによる下書きです。寸法・方位・出入口・申請区画は現地実測で補正してください。",
            insert=(legend_x, A4_H_MM - MARGIN_MM - 4),
            font_size=2.2,
            font_family="sans-serif",
            fill="gray",
        )
    )

    dwg.save()
    return out
