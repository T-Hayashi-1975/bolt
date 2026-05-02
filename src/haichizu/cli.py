"""Command-line interface for the 配置図 generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from haichizu.analyzer import analyze_image
from haichizu.generator import render_svg
from haichizu.maps import fetch_satellite
from haichizu.models import (
    AnalysisResult,
    ApplicantInfo,
    ImageMetadata,
    ParkingSpace,
    Point,
)
from haichizu.validator import validate

app = typer.Typer(
    name="haichizu",
    help="AI-assisted 配置図 generator for 車庫証明 applications.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def fetch(
    lat: Annotated[float, typer.Option(help="駐車場中心の緯度")],
    lng: Annotated[float, typer.Option(help="駐車場中心の経度")],
    out: Annotated[Path, typer.Option(help="保存先 PNG パス")] = Path("output/satellite.png"),
    zoom: Annotated[int, typer.Option(min=15, max=22)] = 20,
) -> None:
    """Google Static Maps から航空写真を取得します。"""
    load_dotenv()
    meta = fetch_satellite(lat, lng, zoom, out)
    console.print(f"[green]✓[/green] 保存: {out} ({meta.width_px}x{meta.height_px}px)")
    meta_path = out.with_suffix(".meta.json")
    meta_path.write_text(meta.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"[green]✓[/green] メタデータ: {meta_path}")


@app.command()
def analyze(
    image: Annotated[Path, typer.Argument(help="航空写真のパス")],
    meta: Annotated[Path, typer.Option(help="ImageMetadata JSON のパス")],
    target: Annotated[str | None, typer.Option(help="申請区画ヒント (任意)")] = None,
    out: Annotated[Path, typer.Option(help="解析結果 JSON 保存先")] = Path(
        "output/analysis.json"
    ),
) -> None:
    """Claude Vision で航空写真を解析します。"""
    load_dotenv()
    image_meta = ImageMetadata.model_validate_json(meta.read_text(encoding="utf-8"))
    console.print(f"[blue]→[/blue] {image} を解析中…")
    result = analyze_image(image, image_meta, target_space_hint=target)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"[green]✓[/green] {len(result.spaces)} 区画を検出")
    console.print(f"[green]✓[/green] 解析結果: {out}")


@app.command()
def generate(
    analysis_path: Annotated[Path, typer.Option("--analysis", help="解析結果 JSON のパス")],
    meta_path: Annotated[Path, typer.Option("--meta", help="ImageMetadata JSON のパス")],
    applicant_path: Annotated[Path, typer.Option("--applicant", help="ApplicantInfo JSON のパス")],
    out: Annotated[Path, typer.Option(help="SVG 出力先")] = Path("output/haichizu.svg"),
) -> None:
    """解析結果から配置図 SVG を生成し、検証を実行します。"""
    analysis = AnalysisResult.model_validate_json(analysis_path.read_text(encoding="utf-8"))
    image_meta = ImageMetadata.model_validate_json(meta_path.read_text(encoding="utf-8"))
    applicant = ApplicantInfo.model_validate_json(applicant_path.read_text(encoding="utf-8"))

    issues = validate(analysis, applicant, image_meta)
    table = Table(title="検証結果")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("Message")
    for issue in issues:
        color = {"error": "red", "warning": "yellow", "info": "cyan"}[issue.severity]
        table.add_row(f"[{color}]{issue.severity}[/{color}]", issue.code, issue.message)
    console.print(table)

    svg_path = render_svg(analysis, applicant, image_meta, issues, out)
    console.print(f"[green]✓[/green] 配置図 SVG: {svg_path}")


@app.command()
def demo(
    out_dir: Annotated[Path, typer.Option(help="出力ディレクトリ")] = Path("output/demo"),
) -> None:
    """API キー不要のダミー解析結果で SVG 生成を試します。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = ImageMetadata(
        center_lat=35.083,
        center_lng=137.156,
        zoom=20,
        width_px=1280,
        height_px=1280,
        scale=2,
        source="user_upload",
    )
    spaces: list[ParkingSpace] = []
    for row in range(2):
        for col in range(8):
            x0 = 200 + col * 100
            y0 = 400 + row * 250
            spaces.append(
                ParkingSpace(
                    id=f"{row + 1}-{col + 1}",
                    polygon=[
                        Point(x=x0, y=y0),
                        Point(x=x0 + 80, y=y0),
                        Point(x=x0 + 80, y=y0 + 200),
                        Point(x=x0, y=y0 + 200),
                    ],
                )
            )
    analysis = AnalysisResult(
        spaces=spaces,
        entrances=[],
        roads=[],
        notes="デモ用ダミーデータ。AI解析は実行されていません。",
        detected_landmarks=["chocoZAP豊田元町"],
    )
    applicant = ApplicantInfo(
        applicant_name="山田 太郎",
        vehicle_make="トヨタ",
        vehicle_model_code="ZSU60W",
        vehicle_length_cm=480,
        vehicle_width_cm=185,
        target_space_id="1-4",
    )
    issues = validate(analysis, applicant, meta)
    svg_path = render_svg(analysis, applicant, meta, issues, out_dir / "haichizu.svg")
    (out_dir / "analysis.json").write_text(
        analysis.model_dump_json(indent=2), encoding="utf-8"
    )
    (out_dir / "meta.json").write_text(meta.model_dump_json(indent=2), encoding="utf-8")
    (out_dir / "applicant.json").write_text(
        applicant.model_dump_json(indent=2), encoding="utf-8"
    )
    console.print(f"[green]✓[/green] デモ生成完了: {svg_path}")
    console.print(json.dumps([i.model_dump() for i in issues], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
