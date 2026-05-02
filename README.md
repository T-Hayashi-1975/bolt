# haichizu — AI-assisted 配置図 generator

行政書士の車庫証明（自動車保管場所証明）申請業務を支援するMVP。
Google Maps の航空写真を Claude Vision で解析し、配置図SVGの下書きを自動生成します。

> **重要：本ツールが生成する配置図はAIによる下書きです。**
> 最終的な寸法・方位・出入口・申請区画の特定は、必ず現地実測のうえ
> 行政書士が確認・補正してください。AIの推定寸法をそのまま申請に
> 使用することは想定していません。

## アーキテクチャ

```
住所/緯度経度 ─▶ Google Static Maps（スケール既知）
                       │
                       ▼
            Claude Vision (sonnet-4-6)
            ・駐車枠検出  ・出入口推定  ・道路特定
                       │
                       ▼
              Pixel→Meter 変換（Web Mercator）
                       │
                       ▼
            ルールエンジン（法令要件チェック）
                       │
                       ▼
              SVG 配置図（A4, 1:100）
```

## モジュール構成

| ファイル | 役割 |
|---|---|
| `src/haichizu/maps.py` | Google Static Maps APIラッパ |
| `src/haichizu/geo.py` | Web Mercator 投影によるピクセル↔メートル変換 |
| `src/haichizu/analyzer.py` | Claude Vision 解析（プロンプトキャッシュ + 構造化出力） |
| `src/haichizu/validator.py` | 法令ルールエンジン（区画寸法・本拠2km等） |
| `src/haichizu/generator.py` | SVG生成（A4縦・1:100） |
| `src/haichizu/cli.py` | typerベースのCLI |
| `src/haichizu/models.py` | Pydanticデータモデル |

## セットアップ

```bash
pip install -e .
cp .env.example .env
# .env に ANTHROPIC_API_KEY と GOOGLE_MAPS_API_KEY を設定
```

## 使い方

### 1. デモ実行（API不要）

ダミー駐車場データでSVG生成を試します。

```bash
haichizu demo
```

`output/demo/haichizu.svg` に配置図が生成されます。

### 2. 本番フロー

```bash
# (a) 航空写真を取得
haichizu fetch --lat 35.083 --lng 137.156 --zoom 20 \
    --out output/lot.png

# (b) Claude Vision で解析
haichizu analyze output/lot.png \
    --meta output/lot.meta.json \
    --target "中央列の左から4番目" \
    --out output/analysis.json

# (c) 配置図を生成
haichizu generate \
    --analysis output/analysis.json \
    --meta output/lot.meta.json \
    --applicant examples/applicant.json \
    --out output/haichizu.svg
```

## Claude API の活用

`src/haichizu/analyzer.py` で以下を実装：

- **モデル**：`claude-sonnet-4-6`（多モーダル + 構造化出力対応、コスト効率）
- **プロンプトキャッシュ**：法令ルール（`LEGAL_RULES`）を `cache_control: ephemeral` で常駐させ、繰り返し呼び出し時のコストを~90%削減
- **構造化出力**：`messages.parse(output_format=AnalysisResult)` で型安全なJSON返却
- **Vision**：base64画像入力で航空写真を直接解析

## 縮尺計算

Google Static Maps の Web Mercator 投影に基づき、ピクセル⇔メートルを決定論的に変換：

```
mpp = 40,075,016.686 × cos(lat) / (256 × 2^zoom × scale)
```

zoom=20, lat=35°, scale=2 で約 0.062 m/px。これにより**航空写真上の概略寸法を実寸換算可能**ですが、配置図に必要な精度（±数cm）には現地実測が不可欠です。

## 検証ルール

`src/haichizu/validator.py` が実行：

| コード | 内容 |
|---|---|
| `target_space_missing` | 申請区画が検出結果に存在しない |
| `space_too_short` | 区画長 < 車長 |
| `space_too_narrow` | 区画幅 < 車幅 |
| `entrance_not_detected` | 出入口未検出 |
| `road_not_detected` | 接道道路未検出 |
| `road_width_unknown` | 道路幅員不明 |
| `ai_draft_disclaimer` | AI下書き注意喚起（常時付与） |

## テスト

```bash
pip install -e .[dev]
pytest
```

## 制限事項

- **配置図の寸法は実測必須** — 航空写真の解像度では±数十cmの誤差
- **屋根付き駐車場は不可** — 上空から見えない
- **道路幅員は推定** — 道路台帳API連携は未実装
- **方位はGoogle Maps前提** — Static Maps APIは常に北上、ユーザーアップロード画像は別途指定要
- **行政書士業務独占** — 本ツールは行政書士事務所の補助ツールであり、最終責任は行政書士が負います

## 今後の拡張余地

- ドローン撮影画像での補完
- 道路台帳API（自治体）連携による道路幅員の自動取得
- モバイルAR測定アプリでの実測値統合
- 路外駐車場届出（駐車場法）への対応
- OSS（自動車保有関係手続のワンストップサービス）連携
