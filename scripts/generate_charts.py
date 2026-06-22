"""Generate sanitized case-study charts from aggregate metrics.

Uses matplotlib only (no seaborn) and no network access. Reads safe aggregate
values from data/aggregate_metrics.json and writes PNG charts into charts/.

Run:
    pip install -r requirements.txt
    python scripts/generate_charts.py
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

# Use a writable cache dir so matplotlib does not warn in restricted/headless
# environments where the default config dir is not writable.
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "mplconfig"))

import matplotlib

matplotlib.use("Agg")  # headless / no display required
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = REPO_ROOT / "data" / "aggregate_metrics.json"
CHARTS_DIR = REPO_ROOT / "charts"

PRIMARY = "#1f3a5f"
ACCENT = "#2a9d8f"
COLORS = ["#1f3a5f", "#2a9d8f", "#e9c46a", "#e76f51", "#264653", "#8ab17d"]


def load_metrics() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def chart_record_volume(metrics: dict) -> Path:
    """Bar chart comparing statute vs. case-law record volumes."""
    labels = ["Statute sections", "Case-law records"]
    values = [
        metrics.get("statute_sections_processed", 0),
        metrics.get("case_law_records_processed", 0),
    ]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, values, color=[PRIMARY, ACCENT], width=0.55)
    ax.set_title("Record Volume Processed", fontsize=14, fontweight="bold")
    ax.set_ylabel("Records")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    ax.margins(y=0.15)
    fig.tight_layout()

    out = CHARTS_DIR / "record_volume_summary.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def chart_platform_scope(metrics: dict) -> Path:
    """Summary of platform scope: states, practice areas, scaling target."""
    states = metrics.get("states_covered", 0)
    practice_areas = metrics.get("practice_areas", 0)
    target_states = 50  # scalable_to_50_states

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))

    # Left: states covered vs. target.
    axes[0].bar(
        ["Covered", "Target"],
        [states, target_states],
        color=[ACCENT, PRIMARY],
        width=0.5,
    )
    axes[0].set_title("US States: Covered vs. Target", fontweight="bold")
    axes[0].set_ylabel("States")
    for i, value in enumerate([states, target_states]):
        axes[0].text(i, value, str(value), ha="center", va="bottom", fontweight="bold")
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)
    axes[0].margins(y=0.15)

    # Right: a single highlighted metric for practice areas.
    axes[1].axis("off")
    axes[1].text(0.5, 0.62, str(practice_areas), ha="center", va="center",
                 fontsize=52, fontweight="bold", color=PRIMARY)
    axes[1].text(0.5, 0.30, "Legal practice areas", ha="center", va="center",
                 fontsize=13)

    fig.suptitle("Platform Scope", fontsize=14, fontweight="bold")
    fig.tight_layout()

    out = CHARTS_DIR / "platform_scope_summary.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def chart_pipeline_stages() -> Path:
    """Horizontal overview of the 8 pipeline stages."""
    stages = [
        "Source discovery",
        "Extraction",
        "Normalization",
        "Validation",
        "Storage",
        "AI enrichment",
        "Analytics",
        "Reporting",
    ]
    y = list(range(len(stages)))[::-1]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(y, [1] * len(stages), color=COLORS * 2, height=0.6)
    for yi, label in zip(y, stages):
        ax.text(0.5, yi, label, ha="center", va="center",
                color="white", fontweight="bold")
    ax.set_title("Data Pipeline Stage Overview", fontsize=14, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.axis("off")
    fig.tight_layout()

    out = CHARTS_DIR / "pipeline_stage_overview.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def main() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics()

    outputs = [
        chart_record_volume(metrics),
        chart_platform_scope(metrics),
        chart_pipeline_stages(),
    ]

    print("Charts generated:")
    for path in outputs:
        print(f"  - {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
