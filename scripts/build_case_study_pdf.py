"""Build the Fiverr Pro PDF case study (premium, agency-grade layout).

Renders a clean, scannable, multi-page PDF from structured, sanitized content
using reportlab. Embeds the pre-generated charts from charts/. No network
access and no production data.

Design system (palette matches scripts/generate_charts.py):
  - deep navy   #1f3a5f  (primary)
  - teal        #2a9d8f  (accent)
  - warm sand   #e9c46a  (chart/callout accent)
  - clay        #e76f51  (chart/callout accent)
  - slate       #264653
  - tints       #f3f7f6 / #f4f4f4 (backgrounds)

Run:
    .venv/bin/python scripts/build_case_study_pdf.py
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# --------------------------------------------------------------------------- #
# Paths & constants
# --------------------------------------------------------------------------- #
REPO_ROOT = Path(__file__).resolve().parents[1]
CHARTS_DIR = REPO_ROOT / "charts"
DIAGRAMS_DIR = REPO_ROOT / "diagrams" / "rendered"
SCREENSHOTS_DIR = REPO_ROOT / "screenshots"
DATA_FILE = REPO_ROOT / "data" / "aggregate_metrics.json"
OUTPUT_PDF = REPO_ROOT / "Legal_Data_Platform_Case_Study_Fiverr_Pro.pdf"

GITHUB_URL = "https://github.com/mlordjames/legal-statute-platform-case-study"
DISCLAIMER = (
    "Due to client confidentiality, the production repository and dataset are "
    "private. This case study includes anonymized architecture, sample outputs, "
    "workflow screenshots, and a sanitized technical summary of the delivered "
    "system."
)

# --------------------------------------------------------------------------- #
# Color system
# --------------------------------------------------------------------------- #
PRIMARY = colors.HexColor("#1f3a5f")   # deep navy
ACCENT = colors.HexColor("#2a9d8f")    # teal
SAND = colors.HexColor("#e9c46a")      # warm sand
CLAY = colors.HexColor("#e76f51")      # clay
SLATE = colors.HexColor("#264653")     # slate
INK = colors.HexColor("#27323d")       # body text
MUTED = colors.HexColor("#5a6b78")     # captions / labels
TINT = colors.HexColor("#f3f7f6")      # light teal-ish background
TINT2 = colors.HexColor("#f4f4f4")     # neutral gray background
CARD_BORDER = colors.HexColor("#dde6e6")
HAIRLINE = colors.HexColor("#cfdada")

PAGE_W, PAGE_H = LETTER
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


# --------------------------------------------------------------------------- #
# Styles
# --------------------------------------------------------------------------- #
def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CSDisclaimer", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=12.5, textColor=colors.HexColor("#48565f"),
    ))
    styles.add(ParagraphStyle(
        name="CSRepo", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=9, leading=12, textColor=PRIMARY,
    ))
    styles.add(ParagraphStyle(
        name="CSEyebrow", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=9, leading=12, textColor=ACCENT, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CSTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=29, leading=33, textColor=PRIMARY, spaceAfter=4,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="CSSubtitle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=12.5, leading=17, textColor=SLATE, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="CSHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14.5, leading=18, textColor=PRIMARY, spaceBefore=2, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="CSBody", parent=styles["Normal"], fontName="Helvetica",
        fontSize=10, leading=15.5, textColor=INK, alignment=TA_LEFT, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CSBullet", parent=styles["Normal"], fontName="Helvetica",
        fontSize=10, leading=14.5, textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="CSCaption", parent=styles["Normal"], fontName="Helvetica-Oblique",
        fontSize=8.5, leading=11.5, textColor=MUTED, alignment=TA_CENTER,
        spaceBefore=5,
    ))
    styles.add(ParagraphStyle(
        name="CSCode", parent=styles["Normal"], fontName="Courier",
        fontSize=8.5, leading=12.5, textColor=colors.HexColor("#1c2a33"),
    ))
    styles.add(ParagraphStyle(
        name="CSCodeLabel", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=7.5, leading=10, textColor=MUTED,
    ))
    styles.add(ParagraphStyle(
        name="CSStatNum", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=21, leading=23, textColor=PRIMARY, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="CSStatLabel", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8, leading=10.5, textColor=MUTED, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="CSCallLead", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, textColor=PRIMARY,
    ))
    styles.add(ParagraphStyle(
        name="CSCallBody", parent=styles["Normal"], fontName="Helvetica",
        fontSize=9.5, leading=13.5, textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="CSArch", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10, leading=15, textColor=SLATE, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="CSChip", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=9, leading=12, textColor=PRIMARY, alignment=TA_CENTER,
    ))
    return styles


# --------------------------------------------------------------------------- #
# Custom flowables
# --------------------------------------------------------------------------- #
class HRule(Flowable):
    """A thin horizontal accent rule."""

    def __init__(self, width, thickness=2, color=ACCENT, space_before=0,
                 space_after=0, left_len=None):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_before = space_before
        self.space_after = space_after
        self.left_len = left_len  # if set, draw a shorter colored segment

    def wrap(self, aw, ah):
        return self.width, self.thickness + self.space_before + self.space_after

    def draw(self):
        c = self.canv
        y = self.space_after
        c.setLineWidth(self.thickness)
        if self.left_len:
            c.setStrokeColor(self.color)
            c.line(0, y, self.left_len, y)
            c.setStrokeColor(HAIRLINE)
            c.setLineWidth(0.6)
            c.line(self.left_len, y, self.width, y)
        else:
            c.setStrokeColor(self.color)
            c.line(0, y, self.width, y)


class SectionHeader(Flowable):
    """Section heading with a small colored tab + accent underline."""

    def __init__(self, text, style, width, tab_color=ACCENT):
        super().__init__()
        self.para = Paragraph(text, style)
        self.style = style
        self.width = width
        self.tab_color = tab_color
        self._h = 0

    def wrap(self, aw, ah):
        self.width = aw
        _, ph = self.para.wrap(aw - 14, ah)
        self._h = ph + 8
        return aw, self._h

    def draw(self):
        c = self.canv
        # colored tab to the left of the heading
        c.setFillColor(self.tab_color)
        c.roundRect(0, self._h - 16, 5, 14, 2, stroke=0, fill=1)
        self.para.drawOn(c, 14, self._h - 18)
        # accent underline
        c.setStrokeColor(self.tab_color)
        c.setLineWidth(1.6)
        c.line(0, 1, 46, 1)
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.6)
        c.line(46, 1, self.width, 1)


class Callout(Flowable):
    """Left-accent-bordered callout: bold lead-in + one sentence."""

    def __init__(self, lead, body, styles, width, accent=ACCENT):
        super().__init__()
        self.accent = accent
        self.width = width
        self.pad = 9
        self.bar = 3.5
        text = f'<b>{lead}</b> &nbsp;{body}'
        self.para = Paragraph(text, styles["CSCallBody"])
        self._h = 0

    def wrap(self, aw, ah):
        self.width = aw
        inner = aw - self.bar - self.pad * 2 - 4
        _, ph = self.para.wrap(inner, ah)
        self._h = ph + self.pad * 2
        return aw, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(TINT)
        c.roundRect(0, 0, self.width, self._h, 4, stroke=0, fill=1)
        c.setFillColor(self.accent)
        c.roundRect(0, 0, self.bar + 2, self._h, 2, stroke=0, fill=1)
        c.setFillColor(TINT)
        c.rect(self.bar, 0, 3, self._h, stroke=0, fill=1)
        self.para.drawOn(c, self.bar + self.pad + 4, self.pad)


class CodeCard(Flowable):
    """Monospace 'Sample — sanitized' card with rounded gray background."""

    def __init__(self, label, code_lines, styles, width):
        super().__init__()
        self.width = width
        self.pad = 10
        self.label = Paragraph(
            f'<font color="#7a8893">{"&#9632;"}</font> &nbsp;SAMPLE &mdash; SANITIZED &nbsp;'
            f'<font color="#9aa7af">| {label}</font>',
            styles["CSCodeLabel"],
        )
        self.code = Paragraph("<br/>".join(code_lines), styles["CSCode"])
        self._h = 0
        self._lh = 0
        self._ch = 0

    def wrap(self, aw, ah):
        self.width = aw
        inner = aw - self.pad * 2
        _, self._lh = self.label.wrap(inner, ah)
        _, self._ch = self.code.wrap(inner, ah)
        self._h = self.pad * 2 + self._lh + 7 + self._ch
        return aw, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#f6f8f9"))
        c.setStrokeColor(CARD_BORDER)
        c.setLineWidth(0.8)
        c.roundRect(0, 0, self.width, self._h, 6, stroke=1, fill=1)
        top = self._h - self.pad
        self.label.drawOn(c, self.pad, top - self._lh)
        c.setStrokeColor(colors.HexColor("#e3e9ea"))
        c.setLineWidth(0.6)
        c.line(self.pad, top - self._lh - 4, self.width - self.pad, top - self._lh - 4)
        self.code.drawOn(c, self.pad, self.pad)


class ChartCard(Flowable):
    """An embedded chart inside a light bordered card with a caption."""

    def __init__(self, image_path, caption, styles, width):
        super().__init__()
        self.width = width
        self.pad = 9
        img = Image(str(image_path))
        ratio = img.imageHeight / float(img.imageWidth)
        iw = width - self.pad * 2
        img.drawWidth = iw
        img.drawHeight = iw * ratio
        self.img = img
        self.caption = Paragraph(caption, styles["CSCaption"])
        self._h = 0
        self._caph = 0

    def wrap(self, aw, ah):
        self.width = aw
        inner = aw - self.pad * 2
        if abs(self.img.drawWidth - inner) > 0.5:
            ratio = self.img.drawHeight / float(self.img.drawWidth)
            self.img.drawWidth = inner
            self.img.drawHeight = inner * ratio
        _, self._caph = self.caption.wrap(inner, ah)
        self._h = self.pad * 2 + self.img.drawHeight + self._caph + 4
        return aw, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(colors.white)
        c.setStrokeColor(CARD_BORDER)
        c.setLineWidth(0.8)
        c.roundRect(0, 0, self.width, self._h, 6, stroke=1, fill=1)
        cap_y = self.pad
        self.caption.drawOn(c, self.pad, cap_y)
        self.img.drawOn(c, self.pad, cap_y + self._caph + 4)


# --------------------------------------------------------------------------- #
# Composite builders
# --------------------------------------------------------------------------- #
def stats_band(styles, metrics, width):
    """Horizontal row of rounded metric cards."""
    cards = [
        (f"{metrics['statute_sections_processed'] // 1000}K+", "Statute sections", PRIMARY),
        (f"{metrics['case_law_records_processed'] // 1000}K+", "Court case records", ACCENT),
        (f"{metrics['states_covered']} states", "TX / FL / NY / CA", CLAY),
        (f"{metrics['practice_areas']}", "Practice areas", SLATE),
    ]

    def cell(num, label, accent):
        inner = Table(
            [[Paragraph(num, styles["CSStatNum"])],
             [Paragraph(label, styles["CSStatLabel"])]],
            colWidths=[width / 4 - 16],
        )
        inner.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
            ("TOPPADDING", (0, 1), (-1, 1), 0),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), TINT),
            ("LINEABOVE", (0, 0), (-1, 0), 3, accent),
            ("BOX", (0, 0), (-1, -1), 0.8, CARD_BORDER),
            ("ROUNDEDCORNERS", [5, 5, 5, 5]),
        ]))
        return inner

    cells = [cell(n, l, a) for n, l, a in cards]
    band = Table([cells], colWidths=[width / 4] * 4)
    band.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return band


def arch_flow(styles, width):
    """Architecture flow as connected chips."""
    stages = ["Sources", "Extractors", "Normalization", "Validation",
              "Storage", "AI Enrichment", "Analytics", "Reports"]
    row = []
    for i, st in enumerate(stages):
        row.append(Paragraph(st, styles["CSChip"]))
        if i < len(stages) - 1:
            row.append(Paragraph('<font color="#2a9d8f">&rarr;</font>', styles["CSChip"]))
    # two rows of 4 chips for readability
    def chip_table(items):
        cells = []
        for it in items:
            cells.append(it)
        t = Table([cells], colWidths=[width / len(cells)] * len(cells))
        stys = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]
        # style chip cells (even indices) as tinted boxes
        for col in range(len(cells)):
            if col % 2 == 0:
                stys.append(("BACKGROUND", (col, 0), (col, 0), TINT))
                stys.append(("BOX", (col, 0), (col, 0), 0.8, ACCENT))
                stys.append(("ROUNDEDCORNERS", [4, 4, 4, 4]))
        t.setStyle(TableStyle(stys))
        return t

    # split into two visual rows
    first = []
    for i, st in enumerate(stages[:4]):
        first.append(Paragraph(st, styles["CSChip"]))
        if i < 3:
            first.append(Paragraph('<font color="#2a9d8f">&rarr;</font>', styles["CSChip"]))
    second = []
    for i, st in enumerate(stages[4:]):
        second.append(Paragraph(st, styles["CSChip"]))
        if i < 3:
            second.append(Paragraph('<font color="#2a9d8f">&rarr;</font>', styles["CSChip"]))

    wrap = Table(
        [[chip_table(first)], [Paragraph('<font color="#2a9d8f">&darr;</font>', styles["CSChip"])],
         [chip_table(second)]],
        colWidths=[width],
    )
    wrap.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return wrap


def tech_stack_grid(styles, width):
    items = ["Python", "Playwright", "AWS S3", "Parquet", "Athena", "Airflow",
             "Claude AI / LLM", "CourtListener", "JSON / CSV", "Validation scripts"]
    cols = 5
    rows = []
    cur = []
    for it in items:
        cur.append(Paragraph(it, styles["CSChip"]))
        if len(cur) == cols:
            rows.append(cur)
            cur = []
    if cur:
        while len(cur) < cols:
            cur.append(Paragraph("", styles["CSChip"]))
        rows.append(cur)
    t = Table(rows, colWidths=[width / cols] * cols)
    stys = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("INNERGRID", (0, 0), (-1, -1), 4, colors.white),
        ("BACKGROUND", (0, 0), (-1, -1), TINT2),
        ("BOX", (0, 0), (-1, -1), 0, colors.white),
    ]
    t.setStyle(TableStyle(stys))
    return t


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(text, style), leftIndent=8, value=None) for text in items],
        bulletType="bullet", bulletColor=ACCENT, start="square",
        leftIndent=14, bulletFontSize=6,
    )


def load_metrics() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# Page furniture (hero header + footer via canvas callbacks)
# --------------------------------------------------------------------------- #
def draw_footer(canvas, doc):
    canvas.saveState()
    y = 0.5 * inch
    canvas.setStrokeColor(HAIRLINE)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, y + 12, PAGE_W - MARGIN, y + 12)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, y, "7 Seer  ·  Multi-State Legal Data Platform")
    canvas.drawRightString(PAGE_W - MARGIN, y, f"Page {canvas.getPageNumber()}")
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(PAGE_W / 2, y, GITHUB_URL)
    canvas.restoreState()


def draw_page(canvas, doc):
    # top accent band on every page
    canvas.saveState()
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, PAGE_H - 8, PAGE_W, 8, stroke=0, fill=1)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, PAGE_H - 8, PAGE_W * 0.32, 8, stroke=0, fill=1)
    canvas.restoreState()
    draw_footer(canvas, doc)


# --------------------------------------------------------------------------- #
# Story
# --------------------------------------------------------------------------- #
def build_story(styles):
    s = styles
    metrics = load_metrics()
    story = []
    W = CONTENT_W

    # === HERO ============================================================== #
    # Rule #1: the very first text element is the exact disclaimer, styled as
    # a subtle boxed note. Rule #2: repo link immediately after.
    disc = Paragraph(DISCLAIMER, s["CSDisclaimer"])
    repo = Paragraph(
        f'Sanitized case study repository &nbsp;'
        f'<a href="{GITHUB_URL}"><font color="#1f3a5f">{GITHUB_URL}</font></a>',
        s["CSRepo"],
    )
    note = Table([[disc], [Spacer(1, 5)], [repo]], colWidths=[W])
    note.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TINT),
        ("BOX", (0, 0), (-1, -1), 0.8, CARD_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    story.append(note)
    story.append(Spacer(1, 18))

    # Title block
    story.append(Paragraph("CONFIDENTIAL LEGAL TECH CLIENT · CASE STUDY", s["CSEyebrow"]))
    story.append(Paragraph("Multi-State Legal Data Platform", s["CSTitle"]))
    story.append(HRule(W, thickness=2.5, color=ACCENT, space_before=4,
                       space_after=2, left_len=70))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Founder &amp; Data Lead, 7 Seer", s["CSSubtitle"]))
    story.append(Paragraph(
        "Turning scattered public legal sources into structured, searchable, "
        "analytics-ready datasets at scale.",
        s["CSBody"],
    ))
    story.append(Spacer(1, 12))

    # Stats band
    story.append(stats_band(s, metrics, W))
    story.append(Spacer(1, 16))

    # === PROJECT SUMMARY =================================================== #
    story.append(SectionHeader("Project Summary", s["CSHeading"], W))
    story.append(Paragraph(
        "The system transformed scattered public legal sources into structured, "
        "searchable, analytics-ready legal datasets. Statutes from multiple states "
        "and hundreds of thousands of court cases were extracted, normalized, "
        "validated, AI-enriched, and stored in a lakehouse-style architecture ready "
        "for SQL analytics and product features.",
        s["CSBody"],
    ))

    # === BUSINESS PROBLEM ================================================== #
    story.append(SectionHeader("Business Problem", s["CSHeading"], W))
    story.append(Paragraph(
        "Public legal data is scattered across many state sources, published in "
        "inconsistent structures, and slow and expensive to process by hand. "
        "Building a clean, search-ready dataset from this raw material &mdash; "
        "reliably and at scale &mdash; was the core challenge.",
        s["CSBody"],
    ))

    # === SOLUTION DELIVERED ================================================ #
    story.append(SectionHeader("Solution Delivered", s["CSHeading"], W))
    sol = [
        "Multi-state statute extraction",
        "Normalized data schemas",
        "AI-generated summaries and metadata",
        "CourtListener bulk data processing",
        "AWS lakehouse-style storage",
        "Parquet / Athena-style analytics",
        "Airflow-style orchestration",
        "Validation and checkpoint / resume workflows",
        "Client-ready reporting",
    ]
    col_w = W / 2 - 6
    left = bullets(sol[:5], s["CSBullet"])
    right = bullets(sol[5:], s["CSBullet"])
    two = Table([[left, right]], colWidths=[col_w + 12, col_w])
    two.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(two)

    # === TECHNICAL ARCHITECTURE =========================================== #
    story.append(Spacer(1, 4))
    story.append(KeepTogether([
        SectionHeader("Technical Architecture", s["CSHeading"], W),
        Paragraph(
            "Extraction is decoupled from enrichment, with a validated record in "
            "between. Data flows through lakehouse zones (raw &rarr; clean &rarr; "
            "enriched), is stored as Parquet, and is queried via an Athena-compatible "
            "SQL layer. The whole flow is orchestrated as discrete, re-runnable tasks.",
            s["CSBody"],
        ),
        Spacer(1, 4),
        arch_flow(s, W),
    ]))
    story.append(Spacer(1, 10))
    story.append(KeepTogether([
        ChartCard(CHARTS_DIR / "pipeline_stage_overview.png",
                  "Eight discrete, re-runnable pipeline stages from source discovery to reporting.",
                  s, W),
    ]))
    story.append(Spacer(1, 10))
    story.append(KeepTogether([
        ChartCard(DIAGRAMS_DIR / "system_architecture.png",
                  "System architecture: 4 states &times; 12 practice areas &rarr; extraction "
                  "&rarr; AI enrichment &rarr; analytics &amp; case-law.",
                  s, W),
    ]))

    # === TECH STACK ======================================================= #
    story.append(Spacer(1, 6))
    story.append(SectionHeader("Tech Stack", s["CSHeading"], W))
    story.append(tech_stack_grid(s, W))

    # === SCALE AND IMPACT ================================================= #
    story.append(Spacer(1, 8))
    story.append(KeepTogether([
        SectionHeader("Scale and Impact", s["CSHeading"], W),
        bullets([
            f"<b>{metrics['statute_sections_processed']:,}+</b> statute sections processed",
            f"<b>{metrics['case_law_records_processed']:,}+</b> court case records processed",
            f"<b>{metrics['states_covered']}</b> US states covered (Texas, Florida, New York, California)",
            f"<b>{metrics['practice_areas']}</b> legal practice areas",
            "Designed to scale toward all <b>50</b> US states",
        ], s["CSBullet"]),
    ]))
    story.append(Spacer(1, 8))
    chart_row = Table(
        [[ChartCard(CHARTS_DIR / "record_volume_summary.png",
                    "Record volume processed: statute sections vs. case-law records.",
                    s, W / 2 - 6),
          ChartCard(CHARTS_DIR / "platform_scope_summary.png",
                    "Platform scope: states covered vs. 50-state target, and practice areas.",
                    s, W / 2 - 6)]],
        colWidths=[W / 2, W / 2],
    )
    chart_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story.append(chart_row)

    # === SELECTED TECHNICAL DECISIONS ===================================== #
    story.append(Spacer(1, 8))
    story.append(SectionHeader("Selected Technical Decisions", s["CSHeading"], W))
    decisions = [
        ("Separating extraction from enrichment",
         "so re-extracting a source never forces costly re-enrichment, and each stage "
         "can be improved independently.", ACCENT),
        ("Checkpoint / resume",
         "so long, interruptible state-level runs continue from the last good point "
         "instead of restarting.", SAND),
        ("Bulk data for case law",
         "instead of slow per-record API crawling &mdash; far faster and gentler for "
         "500k+ records.", CLAY),
        ("Lakehouse-style storage",
         "(S3 + Parquet + Athena) for cheap, serverless, SQL-queryable analytics that "
         "scales with data volume.", PRIMARY),
        ("Production repo kept private",
         "with this sanitized case study published separately to protect client "
         "confidentiality.", SLATE),
    ]
    for lead, body, acc in decisions:
        story.append(Callout(lead, body, s, W, accent=acc))
        story.append(Spacer(1, 6))

    # === ENGINEERING DEEP-DIVE: COURTLISTENER ============================= #
    story.append(PageBreak())
    story.append(SectionHeader(
        "Engineering Deep-Dive: CourtListener at Scale", s["CSHeading"], W))
    story.append(Paragraph(
        "The hardest part of the platform was case law: structuring "
        "<b>~530,000 state court cases</b> from CourtListener&rsquo;s public corpus &mdash; "
        "a dataset whose raw opinion file alone is <b>54&nbsp;GB compressed "
        "(~350&nbsp;GB decompressed)</b>. Making this reliable, cheap, and scalable drove the "
        "most interesting engineering on the project.",
        s["CSBody"],
    ))
    story.append(Spacer(1, 8))
    story.append(KeepTogether([
        ChartCard(DIAGRAMS_DIR / "courtlistener_athena.png",
                  "CourtListener case-law: one-time bzip2&rarr;Parquet &rarr; serverless "
                  "Athena join (~$0.05/run) &rarr; PA scoring.",
                  s, W),
    ]))

    # Bottleneck -> solution table
    cell = ParagraphStyle("CellBody", parent=s["CSCallBody"], fontSize=8.7, leading=11.5)
    hcell = ParagraphStyle("CellHead", parent=s["CSCallLead"], fontSize=9,
                           textColor=colors.white)
    rows = [[Paragraph("Bottleneck", hcell), Paragraph("Final solution", hcell)]]
    bottlenecks = [
        ("REST API caps free use at <b>125 requests/day</b>; ~530k cases need thousands of calls.",
         "Switch to the <b>public bulk download</b> (3 CSVs, ~62&nbsp;GB) &mdash; months of "
         "crawling becomes a one-time copy."),
        ("54&nbsp;GB opinions file is a <b>single non-splittable bzip2 stream</b>; a silent "
         "decompressor crash wrote <b>625 of 530,034 rows</b> and reported success.",
         "<b>S3 + Parquet + Athena</b> &mdash; a managed engine owns the join, parallelism, "
         "retries, and error propagation. ~$0.05/query."),
        ("DuckDB assumes <b>seekable</b> descriptors &mdash; OOM buffering COPY&rarr;S3, "
         "<i>lseek failed</i> on a named pipe.",
         "<b>pyarrow open_csv on a file object</b> &mdash; a true streaming reader, "
         "~200&nbsp;MB peak. 350&nbsp;GB handled on a small box."),
        ("First convert kept <i>plain_text</i> only, but <b>69% of opinions are HTML-only</b> "
         "&rarr; just ~32% case coverage.",
         "<b>Coalesce</b> plain_text + 6 HTML/XML fallbacks into one cleaned raw_text &mdash; "
         "<b>99.98% non-empty</b> over 10.75M opinions."),
        ("Opinions Parquet (~40&ndash;50&nbsp;GB) <b>overflowed the root disk</b> mid-run.",
         "<b>Per-file stream-upload</b> to staging + delete local immediately &mdash; "
         "<b>~512&nbsp;MB disk peak</b> on any volume."),
    ]
    for issue, fix in bottlenecks:
        rows.append([Paragraph(issue, cell), Paragraph(fix, cell)])
    btable = Table(rows, colWidths=[W * 0.46, W * 0.54])
    bstyle = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, CARD_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.8, CARD_BORDER),
        ("LINEAFTER", (0, 0), (0, -1), 0.5, CARD_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            bstyle.append(("BACKGROUND", (0, r), (-1, r), TINT))
    btable.setStyle(TableStyle(bstyle))
    story.append(Spacer(1, 8))
    story.append(btable)

    # Selected code
    story.append(Spacer(1, 12))
    story.append(Paragraph("Selected code", s["CSCallLead"]))
    story.append(Spacer(1, 5))

    fail_code = [
        "# stderr discarded + exit code unchecked =",
        "# a silent crash wrote 625 of 530,034 rows",
        "# but still reported &quot;OK&quot;.",
        "proc = Popen(cmd, stdout=PIPE,",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stderr=DEVNULL)",
        "for row in DictReader(proc.stdout):",
        "&nbsp;&nbsp;&nbsp;&nbsp;...   # ends early, no error",
        "",
        "# FIX: gate on exit code AND on coverage.",
        "if proc.returncode != 0:",
        '&nbsp;&nbsp;&nbsp;&nbsp;raise RuntimeError(&quot;decompress failed&quot;)',
        "if rows_written &lt; expected * 0.8:",
        '&nbsp;&nbsp;&nbsp;&nbsp;raise RuntimeError(&quot;too few rows&quot;)',
    ]
    pyarrow_code = [
        "# bzip2 &rarr; named pipe; pyarrow streams 64MB",
        "# blocks, ~200MB peak. file object (not a",
        "# path) avoids the lseek call.",
        'with open(pipe_path, &quot;rb&quot;) as pipe:',
        "&nbsp;&nbsp;&nbsp;&nbsp;reader = pac.open_csv(",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pipe,",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ReadOptions(block_size=64 &lt;&lt; 20),",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ParseOptions(newlines_in_values=True),",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ConvertOptions(include_columns=COLS))",
        "&nbsp;&nbsp;&nbsp;&nbsp;for batch in reader:",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;writer.write_batch(batch)  # flush now",
    ]
    code_row1 = Table(
        [[CodeCard("fail loudly", fail_code, s, W / 2 - 6),
          CodeCard("pyarrow streaming", pyarrow_code, s, W / 2 - 6)]],
        colWidths=[W / 2, W / 2],
    )
    code_row1.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story.append(KeepTogether(code_row1))
    story.append(Spacer(1, 8))

    sql_code = [
        "UNLOAD (",
        "&nbsp;&nbsp;SELECT o.cluster_id,",
        "&nbsp;&nbsp;&nbsp;&nbsp;array_join(array_agg(o.raw_text), chr(10)) AS raw_text,",
        "&nbsp;&nbsp;&nbsp;&nbsp;oc.case_name, oc.date_filed, d.court_id",
        "&nbsp;&nbsp;FROM cl_opinions o",
        "&nbsp;&nbsp;JOIN cl_clusters oc ON o.cluster_id = oc.id",
        "&nbsp;&nbsp;JOIN cl_dockets  d  ON oc.docket_id = d.id",
        "&nbsp;&nbsp;WHERE d.court_id IN ( :approved_courts )   -- from config",
        "&nbsp;&nbsp;&nbsp;&nbsp;AND oc.date_filed &gt;= DATE '2006-01-01'",
        "&nbsp;&nbsp;&nbsp;&nbsp;AND length(trim(o.raw_text)) &gt; 0",
        "&nbsp;&nbsp;GROUP BY o.cluster_id, oc.case_name, oc.date_filed, d.court_id",
        ") TO 's3://&lt;data-lake&gt;/athena-results/run=&lt;ts&gt;/'",
        "WITH (format='PARQUET', compression='SNAPPY')",
    ]
    story.append(KeepTogether(CodeCard(
        "recurring Athena join &mdash; ~$0.05/run", sql_code, s, W)))

    # Cost engineering
    story.append(Spacer(1, 12))
    story.append(SectionHeader("Cost Engineering", s["CSHeading"], W))
    cost_callouts = [
        ("Ephemeral, auto-terminating compute",
         "conversion runs on a short-lived EC2 box with a <font face='Courier'>--shutdown</font> "
         "flag (<font face='Courier'>sudo shutdown -h now</font>) that self-terminates on "
         "success, never on failure &mdash; no idle instances.", ACCENT),
        ("Disk-bounded streaming + cleanup",
         "each ~512&nbsp;MB Parquet file is uploaded then deleted immediately, so a "
         "multi-hundred-GB job needs ~512&nbsp;MB of disk; staging&rarr;verify&rarr;promote keeps "
         "the canonical dataset clean.", SAND),
        ("Convert once, query forever",
         "bzip2&rarr;Parquet is one-time per monthly snapshot; every query reads the same "
         "column-pruned Parquet (~$0.05) instead of re-downloading 62&nbsp;GB.", CLAY),
        ("Scale-flat querying + planned batch enrichment",
         "adding states is a config change (Athena stays ~$0.05/run for 4 states or 50); "
         "case-law LLM enrichment routes through the Batch API with model right-sizing to "
         "~halve spend.", PRIMARY),
    ]
    for lead, body, acc in cost_callouts:
        story.append(Callout(lead, body, s, W, accent=acc))
        story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>All-in recurring cost: ~$0.40 per run</b> "
        "(Athena ~$0.05 + PA scoring ~$0.09 + S3 writes ~$0.27); one-time Parquet conversion "
        "~$0.43 + ~$1/month storage.",
        s["CSBody"],
    ))

    # === ORCHESTRATION & WORKFLOW ========================================= #
    story.append(PageBreak())
    story.append(KeepTogether([
        SectionHeader("Orchestration &amp; Workflow", s["CSHeading"], W),
        Paragraph(
            "The pipeline runs as three Airflow DAGs, with each stage modeled as a "
            "discrete, re-runnable task so a failure resumes from the last good point. "
            "AI enrichment is <b>dry-run by default</b> and gated behind a manual approval "
            "checkpoint before any paid LLM calls are made.",
            s["CSBody"],
        ),
        Spacer(1, 6),
        ChartCard(DIAGRAMS_DIR / "airflow_orchestration.png",
                  "Airflow orchestration: three DAGs of discrete, re-runnable tasks with a "
                  "manual approval gate before enrichment.",
                  s, W),
    ]))
    story.append(Spacer(1, 10))
    shot_row = Table(
        [[ChartCard(SCREENSHOTS_DIR / "airflow_dags_list.png",
                    "Screenshot from the running Airflow UI: the DAGs list with the three "
                    "pipeline DAGs and their schedules.",
                    s, W / 2 - 6),
          ChartCard(SCREENSHOTS_DIR / "airflow_pipeline_graph.png",
                    "Screenshot from the running Airflow UI: the legal_full_pipeline run "
                    "graph showing per-stage task dependencies.",
                    s, W / 2 - 6)]],
        colWidths=[W / 2, W / 2],
    )
    shot_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story.append(KeepTogether(shot_row))

    # === SAMPLE OUTPUT PREVIEW ============================================ #
    story.append(Spacer(1, 8))
    story.append(SectionHeader("Sample Output Preview", s["CSHeading"], W))
    story.append(Paragraph(
        "Synthetic, sanitized records only &mdash; the full raw_text field is excluded.",
        s["CSBody"],
    ))
    rec_code = [
        "{",
        '&nbsp;&nbsp;"state": "texas",',
        '&nbsp;&nbsp;"practice_area": "landlord_tenant",',
        '&nbsp;&nbsp;"chapter": "Property Code Chapter 92",',
        '&nbsp;&nbsp;"section_id": "sample_section_001",',
        '&nbsp;&nbsp;"title": "Sample Residential Tenancy",',
        '&nbsp;&nbsp;"extraction_status": "validated"',
        "}",
    ]
    enr_code = [
        "{",
        '&nbsp;&nbsp;"section_id": "sample_section_001",',
        '&nbsp;&nbsp;"summary": "Plain-English summary',
        '&nbsp;&nbsp;&nbsp;&nbsp;for search and user understanding.",',
        '&nbsp;&nbsp;"intent_tags": ["tenant_rights",',
        '&nbsp;&nbsp;&nbsp;&nbsp;"lease_compliance",',
        '&nbsp;&nbsp;&nbsp;&nbsp;"notice_requirements"],',
        '&nbsp;&nbsp;"complexity_level": "medium",',
        '&nbsp;&nbsp;"validation_status": "passed"',
        "}",
    ]
    code_row = Table(
        [[CodeCard("statute record", rec_code, s, W / 2 - 6),
          CodeCard("enrichment output", enr_code, s, W / 2 - 6)]],
        colWidths=[W / 2, W / 2],
    )
    code_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story.append(KeepTogether(code_row))

    # === CONFIDENTIALITY NOTE ============================================= #
    story.append(Spacer(1, 8))
    story.append(SectionHeader("Confidentiality Note", s["CSHeading"], W))
    story.append(Paragraph(
        "Production code, datasets, client details, credentials, raw legal text, and "
        "private prompts are excluded. This document and its repository contain only "
        "sanitized architecture, synthetic samples, diagrams, and summaries.",
        s["CSBody"],
    ))

    # === ABOUT 7 SEER ===================================================== #
    story.append(SectionHeader("About 7 Seer", s["CSHeading"], W))
    about = Paragraph(
        "7 Seer builds data pipelines, automation systems, AI-enriched datasets, and "
        "cloud data platforms for businesses that need reliable data collection, "
        "processing, and analytics.",
        s["CSBody"],
    )
    about_box = Table([[about]], colWidths=[W])
    about_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    about_white = ParagraphStyle(
        "AboutWhite", parent=s["CSBody"], textColor=colors.white)
    about_box = Table([[Paragraph(
        "7 Seer builds data pipelines, automation systems, AI-enriched datasets, and "
        "cloud data platforms for businesses that need reliable data collection, "
        "processing, and analytics.", about_white)]], colWidths=[W])
    about_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(about_box)

    # === PROJECT CREDITS ================================================== #
    credit_label = ParagraphStyle(
        "CreditLabel", parent=s["CSCallLead"], fontSize=9.5, leading=13)
    credit_value = ParagraphStyle(
        "CreditValue", parent=s["CSBody"], fontSize=9.5, leading=13, spaceAfter=0)
    credit_rows = [
        ("Project Developer", "Etiese James &mdash; Lead Data Engineer, 7 Seer"),
        ("Lead Agent", "Claude Code (Opus 4.8)"),
        ("Reviewer Agent", "OpenAI GPT"),
    ]
    credits_tbl = Table(
        [[Paragraph(lbl, credit_label), Paragraph(val, credit_value)]
         for lbl, val in credit_rows],
        colWidths=[1.7 * inch, W - 1.7 * inch],
    )
    credits_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TINT),
        ("BOX", (0, 0), (-1, -1), 0.8, CARD_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, HAIRLINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    story.append(KeepTogether([
        Spacer(1, 14),
        SectionHeader("Project Credits", s["CSHeading"], W),
        credits_tbl,
    ]))

    return story


# --------------------------------------------------------------------------- #
# Document assembly
# --------------------------------------------------------------------------- #
def main() -> None:
    styles = build_styles()

    doc = BaseDocTemplate(
        str(OUTPUT_PDF), pagesize=LETTER,
        topMargin=MARGIN + 6, bottomMargin=MARGIN,
        leftMargin=MARGIN, rightMargin=MARGIN,
        title="Multi-State Legal Data Platform - Case Study",
        author="7 Seer",
        subject="Sanitized case study",
    )

    frame = Frame(
        MARGIN, MARGIN, CONTENT_W, PAGE_H - MARGIN - (MARGIN + 6),
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id="main",
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=draw_page),
    ])

    story = build_story(styles)
    doc.build(story)
    print(f"PDF generated: {OUTPUT_PDF.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
