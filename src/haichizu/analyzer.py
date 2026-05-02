"""Claude Vision analysis of aerial parking-lot images.

Uses claude-sonnet-4-6 with prompt caching for the legal context, structured
outputs for typed JSON back, and the multimodal image input format.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

import anthropic

from haichizu.models import AnalysisResult, ImageMetadata

MODEL = "claude-sonnet-4-6"

# Cached system context — stable across requests so it caches cleanly.
LEGAL_RULES = """\
あなたは日本の車庫証明（自動車保管場所証明）申請における配置図作成の専門家です。
航空写真を分析し、配置図に必要な要素を抽出します。

## 配置図の法定要件（自動車の保管場所の確保等に関する法律施行規則）
1. 駐車場の外周形状と寸法（メートル単位）
2. 申請対象区画の特定（番号・位置）
3. 駐車枠の寸法（標準：幅2.5m × 奥行5.0m）
4. 出入口の位置と幅員
5. 接道する道路の位置と幅員
6. 方位（北を示す矢印）
7. 隣接建物の概略

## 重要な制約
- 使用の本拠から保管場所まで直線距離2km以内
- 道路から支障なく出入りできること
- 自動車全体を収容できること

## 画像解析の留意点
- Google Static Maps の航空写真は常に「北が上」
- 駐車枠の白線は薄い場合がある
- 屋根・樹木による遮蔽部分は推定不可と明示する
- 寸法は必ず現地実測が必要であり、AIの推定値は下書きと位置づける
"""

SYSTEM_INSTRUCTIONS = """\
航空写真から駐車場の構造をJSON形式で抽出してください。
- 検出できないものは空配列または null を返す
- 推定の不確かさは notes に記述する
- 座標はピクセル単位（原点：画像左上、X右向き正、Y下向き正）
- 駐車枠の polygon は時計回りに4頂点（矩形を想定）
"""


def _load_image_b64(path: str | Path) -> tuple[str, str]:
    """Return (base64_data, media_type) for the image at *path*."""
    p = Path(path)
    suffix = p.suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix)
    if media_type is None:
        raise ValueError(f"Unsupported image format: {suffix}")
    data = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    return data, media_type


def _user_prompt(meta: ImageMetadata, target_space_hint: str | None) -> str:
    target_clause = (
        f"申請対象区画は「{target_space_hint}」付近です。is_target=true を設定してください。\n"
        if target_space_hint
        else "申請対象区画は別途指定されるため、すべての区画で is_target=false としてください。\n"
    )
    return (
        f"画像メタデータ：\n"
        f"- 中心座標: ({meta.center_lat}, {meta.center_lng})\n"
        f"- ズーム: {meta.zoom}\n"
        f"- サイズ: {meta.width_px}x{meta.height_px} px\n"
        f"- 画像出典: {meta.source}\n\n"
        f"{target_clause}\n"
        "この航空写真を分析し、駐車枠・出入口・接道道路・ランドマークを抽出してください。"
    )


def analyze_image(
    image_path: str | Path,
    image_meta: ImageMetadata,
    *,
    target_space_hint: str | None = None,
    api_key: str | None = None,
) -> AnalysisResult:
    """Analyze an aerial image and return a typed AnalysisResult.

    Uses prompt caching on the legal context so repeated calls within a session
    pay ~0.1× for the cached prefix instead of full input price.
    """
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    image_b64, media_type = _load_image_b64(image_path)
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.parse(
        model=MODEL,
        max_tokens=8192,
        system=[
            {
                "type": "text",
                "text": LEGAL_RULES,
                "cache_control": {"type": "ephemeral"},
            },
            {"type": "text", "text": SYSTEM_INSTRUCTIONS},
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": _user_prompt(image_meta, target_space_hint)},
                ],
            }
        ],
        output_format=AnalysisResult,
    )
    return response.parsed_output
