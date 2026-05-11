"""LinkedIn-optimized hero figure for NOR-TAX.

Designed for the LinkedIn scroll-stopping moment:
  - Square-ish aspect ratio (works on mobile feeds)
  - Big, bold numbers
  - One headline
  - One sub-story
  - Minimal text

The story in three numbers (GPT-4o, 128K context window):
  - 348 sider engelsk innhold
  - 256 sider norsk innhold       (-27%)
  - 295 sider norsk på NorMistral (+18% over Qwen-norsk)

Output:
    paper/figures/linkedin_hero.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

from lib.config import FIGURES_DIR, RUNS_DIR


# Tenki brand palette
COL_BG       = "#FAFAFA"
COL_INK      = "#0F0F12"
COL_MUTED    = "#6E6E76"
COL_SUBTLE   = "#E2E2E2"
COL_ACCENT   = "#1A4DFF"  # Tenki blue
COL_RED      = "#d62728"
COL_GREEN    = "#1A8A3A"


def main() -> None:
    fit = json.loads((RUNS_DIR / "context_fit.json").read_text(encoding="utf-8"))

    # Numbers (GPT-4o 128K window)
    en_pages   = fit["gpt-4o::en"]["windows"]["128K"]["pages_fit"]
    nb_pages   = fit["gpt-4o::nb"]["windows"]["128K"]["pages_fit"]
    norm_pages = fit["normistral-7b::nb"]["windows"]["128K"]["pages_fit"]

    # 4:5 aspect (LinkedIn-friendly mobile-first portrait)
    fig = plt.figure(figsize=(8, 10), dpi=160)
    fig.patch.set_facecolor(COL_BG)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(COL_BG)

    # =========================================================
    # TOP — Eyebrow + headline
    # =========================================================
    ax.text(
        0.06, 0.94, "NOR-TAX  ·  TOKENIZATION-SKATTEN",
        fontsize=12, color=COL_MUTED, family="monospace",
        fontweight=500,
    )

    # Headline — the NOR-TAX framing
    loss_pct = int(round((en_pages - nb_pages) / en_pages * 100))
    ax.text(
        0.06, 0.86, f"{loss_pct} % skatt",
        fontsize=54, color=COL_RED, fontweight=700,
        family="DejaVu Sans",
    )
    ax.text(
        0.06, 0.79, "på å være norsk",
        fontsize=34, color=COL_INK, fontweight=600,
        family="DejaVu Sans",
    )
    ax.text(
        0.06, 0.74, "i KI-en.",
        fontsize=34, color=COL_INK, fontweight=600,
        family="DejaVu Sans",
    )

    # =========================================================
    # MIDDLE — The three bars
    # =========================================================
    # Layout: vertical bars at ~y=0.30 to y=0.65 area, three rows
    # Each row = a "container" representing the 128K window, with the
    # actual content filled in.

    max_pages = max(en_pages, nb_pages, norm_pages)
    bar_left = 0.06
    bar_max_right = 0.78
    bar_height = 0.06
    label_x = bar_left - 0.005
    value_x = 0.95

    rows = [
        ("GPT-4o · engelsk",      en_pages,   COL_ACCENT, "baseline"),
        ("GPT-4o · norsk",        nb_pages,   COL_RED,    f"-{loss_pct} % effektivt vindu"),
        ("NorMistral · norsk",    norm_pages, COL_GREEN,  "+18 % over engelsk"),
    ]

    y0 = 0.62
    gap = 0.13
    for i, (label, pages, color, sub) in enumerate(rows):
        y = y0 - i * gap

        # Container background (representing full 128K window)
        ax.add_patch(Rectangle(
            (bar_left, y - bar_height / 2),
            bar_max_right - bar_left,
            bar_height,
            facecolor=COL_SUBTLE,
            edgecolor="none",
        ))

        # Filled portion (representing pages that actually fit)
        fill_width = (pages / max_pages) * (bar_max_right - bar_left)
        ax.add_patch(Rectangle(
            (bar_left, y - bar_height / 2),
            fill_width,
            bar_height,
            facecolor=color,
            edgecolor="none",
        ))

        # Row label (above bar)
        ax.text(
            bar_left, y + bar_height / 2 + 0.012,
            label,
            fontsize=12, color=COL_INK, fontweight=600,
            family="DejaVu Sans",
        )

        # Big page number (to right of bar)
        ax.text(
            value_x, y,
            f"{pages:.0f}",
            fontsize=30, color=color, fontweight=700,
            family="DejaVu Sans",
            ha="right", va="center",
        )
        ax.text(
            value_x, y - 0.034,
            "sider",
            fontsize=10, color=COL_MUTED, fontweight=500,
            family="monospace",
            ha="right", va="center",
        )

        # Sub-annotation under bar
        ax.text(
            bar_left, y - bar_height / 2 - 0.018,
            sub,
            fontsize=10, color=COL_MUTED, fontweight=500,
            family="DejaVu Sans", fontstyle="italic",
        )

    # =========================================================
    # MIDDLE-BOTTOM — Explanation
    # =========================================================
    ax.text(
        0.06, 0.20,
        "Et 128K context-vindu = ~348 sider engelsk innhold.",
        fontsize=13, color=COL_INK, fontweight=500,
        family="DejaVu Sans",
    )
    ax.text(
        0.06, 0.165,
        "Samme vindu = bare 256 sider norsk på GPT-4o.",
        fontsize=13, color=COL_INK, fontweight=500,
        family="DejaVu Sans",
    )
    ax.text(
        0.06, 0.13,
        "En norsk-trent tokenizer (NorMistral) snur regnestykket.",
        fontsize=13, color=COL_GREEN, fontweight=600,
        family="DejaVu Sans",
    )

    # =========================================================
    # BOTTOM — Attribution
    # =========================================================
    ax.text(
        0.06, 0.05,
        "Måling: 200 FLORES-200-setninger, parret BM/NB/EN-innhold",
        fontsize=10, color=COL_MUTED, fontweight=500,
        family="monospace",
    )
    ax.text(
        0.06, 0.025,
        "github.com/triceraz/dia-tax  ·  Tenki Labs",
        fontsize=10, color=COL_MUTED, fontweight=500,
        family="monospace",
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out = FIGURES_DIR / "linkedin_hero.png"
    fig.savefig(out, dpi=160, facecolor=COL_BG)
    plt.close(fig)
    print(f"[05] -> {out}")


if __name__ == "__main__":
    main()
