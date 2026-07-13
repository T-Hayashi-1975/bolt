# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

JP_FONT = "游ゴシック"
ACCENT = RGBColor(0xC0, 0x00, 0x00)  # 落ち着いた赤（ブランドアクセント）
GRAY = RGBColor(0x44, 0x44, 0x44)

doc = Document()

# 既定フォント（英数＋日本語）
style = doc.styles["Normal"]
style.font.name = "Yu Gothic"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), JP_FONT)

# ページ余白
for section in doc.sections:
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)


def set_jp(run, size=None, bold=False, color=None):
    run.font.name = "Yu Gothic"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), JP_FONT)
    if size:
        run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def para(text="", size=10.5, bold=False, color=None, align=None, space_after=6, space_before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if align is not None:
        p.alignment = align
    if text:
        r = p.add_run(text)
        set_jp(r, size=size, bold=bold, color=color)
    return p


def rich(segments, size=10.5, align=None, space_after=6, space_before=0):
    """segments: list of (text, bold) tuples"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if align is not None:
        p.alignment = align
    for text, bold in segments:
        r = p.add_run(text)
        set_jp(r, size=size, bold=bold)
    return p


def heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    # 左に赤いバー風の罫線
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "24")
    left.set(qn("w:space"), "8")
    left.set(qn("w:color"), "C00000")
    pbdr.append(left)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), "BFBFBF")
    pbdr.append(bottom)
    pPr.append(pbdr)
    r = p.add_run(text)
    set_jp(r, size=13, bold=True, color=ACCENT)
    return p


def hr():
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "D9D9D9")
    pbdr.append(bottom)
    pPr.append(pbdr)


# ===== ヘッダー部 =====
para("報道関係者各位", size=9.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=0)
p = para(align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)
r = p.add_run("2026年6月4日"); set_jp(r, size=9.5, color=GRAY)
p = para(align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=10)
r = p.add_run("株式会社ファイテック"); set_jp(r, size=9.5, color=GRAY)

# プレスリリース ラベル
p = para(space_after=8)
r = p.add_run("PRESS RELEASE")
set_jp(r, size=9, bold=True, color=ACCENT)

# ===== タイトル =====
p = para(space_after=4)
r = p.add_run("代表取締役 林 富徳が『REC AWARD 2026』にて")
set_jp(r, size=16, bold=True)
p = para(space_after=8)
r = p.add_run("「2026年を牽引する34人の経営者」に選出")
set_jp(r, size=16, bold=True)

p = para(space_after=12)
r = p.add_run("―「森林火災をゼロに」を掲げ、消火技術の研究開発で防災・減災と環境対応の両立に挑む―")
set_jp(r, size=11, bold=True, color=ACCENT)

# ===== リード =====
rich([
    ("消防関連の化学製品メーカーである株式会社ファイテック（本社：愛知県丹羽郡大口町、代表取締役：林 富徳）は、当社代表取締役 林 富徳が、毎日新聞出版『週刊エコノミスト増刊 REC AWARD 2026』において、次代を担う経営者を選ぶ", False),
    ("「2026年を牽引する34人の経営者」", True),
    ("の一人に選出されたことをお知らせいたします。", False),
])

para("本企画は、社会や産業が大きく変化する時代にあって、社会課題と向き合いながら新たな価値創造に挑む経営者に焦点を当てるものです。今回の選出は、林 富徳が消火剤メーカーの経営者として研究開発を主導し、家庭の初期消火から大規模な林野火災対策、さらには環境配慮型の製品づくりまで、防災・減災分野で新たな可能性を切り拓いてきた姿勢が評価されたものと受け止めております。")

rich([
    ("当社は、独自の消火剤開発力を強みに、その事業を", False),
    ("海外48か国", True),
    ("へと広げてまいりました。今回の選出を新たな出発点として、「森林火災をゼロに」というビジョンの実現に向け、研究開発を一層加速してまいります。", False),
])

hr()

# ===== 防災・減災の重要性 =====
heading("防災・減災の重要性 ― 多様化する火災リスク")
para("近年、住宅や事業所など私たちの身近な場所で発生する火災に加え、林野火災や大規模災害など、火災リスクはますます多様化しています。また、夏場の気温上昇に伴いエアコンや室外機の使用機会が増えることで、電気機器に起因する火災への備えも一層重要になっています。")
para("火災による被害を最小限に抑えるには、発生直後の初期対応や延焼抑制に加え、日頃から備えやすい防災用品の普及、そして現場の課題に応える消火剤・消火用具の進化が欠かせません。こうした状況のもと、消火剤メーカーには、単に製品を供給するだけでなく、火災の種類や現場環境に応じた製品開発を通じて、防災・減災の実効性と安全性を高めていく役割が求められています。")

# ===== 評価された背景 =====
heading("評価された背景 ― 現場に根ざした研究開発力")
para("林 富徳は、消火剤メーカーの経営者として、家庭や事業所での初期消火から、大規模火災・林野火災への対応まで、幅広い火災リスクと向き合ってまいりました。")
rich([
    ("その姿勢は、現場ごとに異なる課題に応える製品群に結実しています。家庭や事業所の初期消火を補助する「投てき用消火用具」をはじめ、林野火災対策では、延焼抑制と再燃防止を目的とした森林火災用消火剤", False),
    ("「FOREST DEFENDER（フォレストディフェンダー）」", True),
    ("を開発するなど、社会課題化する火災リスクへの対応を進めています。", False),
])
rich([
    ("さらに、社会的関心が高まる", False),
    ("PFAS（有機フッ素化合物類）への対応", True),
    ("も、消火剤メーカーとして重要な使命と捉えています。当社は安全性と環境への配慮を重視した製品づくりを進め、消火性能だけでなく社会的要請に応える研究開発に力を注いでいます。", False),
])
para("こうした、専門性を磨きながら防災・減災分野に新たな価値を生み出そうとする経営姿勢が、今回の選出につながったものと考えております。")

# ===== 取り組み =====
heading("株式会社ファイテックの取り組み")
para("ファイテックは、火災の種類や発生場所によって求められる消火性能が異なることに着目し、家庭用から業務用、産業用、林野火災対策まで、あらゆる現場に対応する製品づくりに取り組んでいます。")
rich([
    ("主な製品には、家庭や事業所の初期消火を補助する「ファイテック投てき用消火用具」、天ぷら油火災に対応する消火剤、業務用厨房向け消火剤、林野火災対策向けの森林火災用消火剤「FOREST DEFENDER」、ヘリコプター用消火剤注入システム", False),
    ("「FEI（Fitech Easy Injection）」", True),
    ("などがあります。", False),
])
para("これらの取り組みは、製品ラインナップを広げることにとどまらず、多様化する火災リスクに対して、消火剤メーカーとしてどのような価値を社会に提供できるかを追求するものです。当社は研究開発を重視するメーカーとして、消火性能の向上と使いやすさを両立し、現場で真に役立つ製品づくりを進めてまいります。")

# ===== PFAS =====
heading("PFASへの対応について")
para("近年、PFAS（有機フッ素化合物類）への社会的関心が高まるなか、消火剤メーカーには、消火性能だけでなく安全性や環境への配慮を踏まえた製品開発が求められています。")
rich([
    ("当社は、環境負荷の低減に配慮した消火剤・消火用具の研究開発を進めており、", False),
    ("当社が開発・製造する消火薬剤にはPFAS（有機フッ素化合物類）を使用しておりません。", True),
    (" 今後も、消火性能・安全性・環境配慮の3つの観点から研究開発を重ね、社会的要請に応える製品づくりに取り組んでまいります。", False),
])

# ===== 今後の展望 =====
heading("今後の展望")
para("火災リスクは、家庭、職場、地域、自然環境など、あらゆる場所に存在しています。当社は、その一つひとつの現場に向き合い、消火性能の向上と使いやすさを両立した製品開発を通じて、火災による被害の軽減に貢献してまいります。")
rich([
    ("今回の選出を励みに、ファイテックは林 富徳のもと、消火剤メーカーとしての研究開発力をさらに高めてまいります。そして、国内外で高まる防災・減災への関心に応えるべく、", False),
    ("日本発の消火剤メーカー", True),
    ("として、消火技術の研究開発と製品づくりを通じ、命と暮らしを守る、より安全で安心な社会の実現に挑戦してまいります。", False),
])

# ===== 代表コメント =====
heading("代表取締役 林 富徳 コメント")


def quote(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "10")
    left.set(qn("w:color"), "D9D9D9")
    pbdr.append(left)
    pPr.append(pbdr)
    r = p.add_run(text)
    set_jp(r, size=10.5, color=GRAY)


quote("このたび『REC AWARD 2026』において「2026年を牽引する34人の経営者」の一人に選出いただき、大変光栄に存じます。")
quote("ここまで歩みを進めてこられたのは、ファイテックの仲間、お客様、パートナーの皆様、そして日頃より支えてくださる多くの方々のおかげです。心より感謝申し上げます。")
quote("今回の選出をゴールではなく、新たなスタートラインと受け止め、今後も消火技術の研究開発を通じて、防災・減災に貢献できる製品づくりに一層努めてまいります。引き続き、ご指導ご鞭撻のほど、何卒よろしくお願い申し上げます。")

# ===== REC AWARD =====
heading("『REC AWARD 2026』について")
para("『REC AWARD 2026』は、毎日新聞出版『週刊エコノミスト増刊』として発行された企画号です。社会や産業が大きく変化する時代において、未来を切り拓く経営者に焦点を当て、「2026年を牽引する34人の経営者」を紹介しています。")

# ===== 会社について =====
heading("株式会社ファイテックについて")
rich([
    ("株式会社ファイテックは、愛知県丹羽郡大口町に本社を構える消防関連の化学製品メーカーです。消防・防災の分野で培った技術力をもとに各種消火剤・消火用具を開発・製造し、現在その事業は", False),
    ("海外48か国", True),
    ("にまで展開しています。", False),
])
para("主力製品には、「ファイテック投てき用消火用具」、天ぷら油用消火剤「箱のまま入れるだけ」、業務用消火スプレー「フライングジェット」などがあり、消防車向け・金属火災向け・林野火災向けの各種消火剤の開発・製造も手掛けるなど、現場のニーズに応じた幅広いラインナップを提供しています。このほか、AI・IT技術を活用し、宅配ボックスの暗証番号を安全に管理するAIパスワード管理システム「Passluck（パスラック）」の開発・運営も行っています。")
rich([
    ("当社の強みは、独自技術による消火剤開発力にあります。特殊な消火剤の独自開発に加え、", False),
    ("消防研究所との共同開発", True),
    ("などを通じて消火技術の向上に努めてまいりました。また、", False),
    ("自衛隊の協力のもとヘリコプター用消火剤注入システム「FEI（Fitech Easy Injection）」を開発", True),
    ("し、同システムは陸上自衛隊が実施する林野火災対策でも活用されています。なお、当社が開発・製造する消火薬剤にはPFAS（有機フッ素化合物類）を使用しておりません。", False),
])

# ===== 会社概要テーブル =====
para("【会社概要】", size=10.5, bold=True, space_before=6, space_after=4)
rows = [
    ("商号", "株式会社ファイテック"),
    ("代表者", "林 富徳"),
    ("所在地", "愛知県丹羽郡大口町秋田3-101"),
    ("設立", "2010年"),
    ("資本金", "4,800万円"),
    ("事業内容", "消防関連化学製品製造業"),
    ("URL", "https://fitech911.com/"),
]
table = doc.add_table(rows=len(rows), cols=2)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.LEFT
for i, (k, v) in enumerate(rows):
    c0 = table.rows[i].cells[0]
    c1 = table.rows[i].cells[1]
    c0.width = Cm(3.5)
    c1.width = Cm(12.0)
    p0 = c0.paragraphs[0]
    r0 = p0.add_run(k); set_jp(r0, size=10, bold=True)
    # ヘッダーセルに薄いグレー背景
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F2F2F2")
    c0._tc.get_or_add_tcPr().append(shd)
    p1 = c1.paragraphs[0]
    r1 = p1.add_run(v); set_jp(r1, size=10)

# ===== 所属団体 =====
para("【所属団体】", size=10.5, bold=True, space_before=10, space_after=4)
para("（NPO法人）国連支援交流協会／（一社）防災安全協会／（一社）全国消防機器販売業協会／（一財）日本森林林業振興会 森林火災対策協会／（公社）日本火災学会／（一社）日本建築学会／（一社）マンション防災協会", size=10, space_after=2)
para("※当社はこれらの団体を通じて、防災技術の研究・普及活動にも積極的に取り組んでいます。", size=9, color=GRAY)

# ===== お問い合わせ =====
hr()
para("【本件に関するお問い合わせ】", size=10.5, bold=True, space_before=6, space_after=4)
para("株式会社ファイテック 広報担当", size=10, space_after=0)
para("メールアドレス：pr@fitech911.com", size=10, space_after=0)
para("プレスリリース一覧：https://prtimes.jp/main/html/searchrlp/company_id/48262", size=10)

out = "/home/user/bolt/ファイテック_REC_AWARD_2026_プレスリリース.docx"
doc.save(out)
print("saved:", out)
