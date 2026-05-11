"""Build the LinkedIn-ready figure for DIA-TAX.

Two-panel layout:
  LEFT  — tokens-per-word per (model, lang): the "tax" itself.
  RIGHT — pages of content that fit in a 128K window: the practical
          consequence.

NorMistral is highlighted because it REVERSES the tax — a Norwegian-trained
tokenizer makes Norwegian cheaper than English.

Output:
    paper/figures/tokenization_tax.png   — the headline figure
    paper/figures/skyline.png            — alternative cleaner skyline
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib.config import FIGURES_DIR, RUNS_DIR


COL_BG       = "#FAFAFA"
COL_INK      = "#0F0F12"
COL_MUTED    = "#6E6E76"
COL_SUBTLE   = "#E2E2E2"
COL_EN       = "#1A4DFF"
COL_NB       = "#d62728"
COL_NN       = "#7A4FE0"
COL_HIGHLIGHT = "#1A8A3A"  # green for the "fix" — NorMistral


# Order on x-axis. NorMistral last so it reads as the punchline.
MODEL_ORDER = ["gpt-4o", "gpt-4-legacy", "qwen-2.5-1.5b", "normistral-7b"]
MODEL_LABEL = {
    "gpt-4o":         "GPT-4o",
    "gpt-4-legacy":   "GPT-4",
    "qwen-2.5-1.5b":  "Qwen 2.5 1.5B",
    "normistral-7b":  "NorMistral 7B",
}


def main() -> None:
    summary = json.loads((RUNS_DIR / "summary_per_lang.json").read_text(encoding="utf-8"))
    fit     = json.loads((RUNS_DIR / "context_fit.json").read_text(encoding="utf-8"))

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(13.5, 5.6))
    fig.patch.set_facecolor(COL_BG)
    ax_l.set_facecolor(COL_BG)
    ax_r.set_facecolor(COL_BG)

    # ============================================================
    # LEFT: tokens-per-word (the "tax" itself)
    # ============================================================
    n = len(MODEL_ORDER)
    width = 0.26
    xs = list(range(n))

    en_vals = [summary[f"{m}::en"]["tokens_per_word_median"] for m in MODEL_ORDER]
    nb_vals = [summary[f"{m}::nb"]["tokens_per_word_median"] for m in MODEL_ORDER]
    nn_vals = [summary[f"{m}::nn"]["tokens_per_word_median"] for m in MODEL_ORDER]

    ax_l.bar([x - width for x in xs], en_vals, width, color=COL_EN,
             label="English", edgecolor="none")
    ax_l.bar(xs,                       nb_vals, width, color=COL_NB,
             label="Norsk (Bokmål)", edgecolor="none")
    ax_l.bar([x + width for x in xs], nn_vals, width, color=COL_NN,
             label="Norsk (Nynorsk)", edgecolor="none")

    # Annotate the bars
    for i, (en, nb, nn) in enumerate(zip(en_vals, nb_vals, nn_vals)):
        ax_l.text(i - width, en + 0.04, f"{en:.2f}", ha="center", fontsize=9, color=COL_INK)
        ax_l.text(i,         nb + 0.04, f"{nb:.2f}", ha="center", fontsize=9, color=COL_INK)
        ax_l.text(i + width, nn + 0.04, f"{nn:.2f}", ha="center", fontsize=9, color=COL_INK)

    ax_l.set_xticks(xs)
    ax_l.set_xticklabels([MODEL_LABEL[m] for m in MODEL_ORDER], fontsize=10)
    ax_l.set_ylabel("Tokens per ord (lavere = billigere)")
    ax_l.set_title("Hvor mange tokens koster ett ord?", fontsize=11, color=COL_INK)
    ax_l.spines["top"].set_visible(False)
    ax_l.spines["right"].set_visible(False)
    ax_l.grid(axis="y", alpha=0.25)
    ax_l.legend(loc="upper right", frameon=False, fontsize=9)
    ax_l.set_ylim(0, max(max(nb_vals), max(nn_vals)) + 0.6)

    # Highlight NorMistral
    norm_idx = MODEL_ORDER.index("normistral-7b")
    ax_l.axvspan(norm_idx - 0.45, norm_idx + 0.45, color=COL_HIGHLIGHT, alpha=0.08, zorder=0)

    # ============================================================
    # RIGHT: pages of content in a 128K window
    # ============================================================
    en_pages = [fit[f"{m}::en"]["windows"]["128K"]["pages_fit"] for m in MODEL_ORDER]
    nb_pages = [fit[f"{m}::nb"]["windows"]["128K"]["pages_fit"] for m in MODEL_ORDER]
    nn_pages = [fit[f"{m}::nn"]["windows"]["128K"]["pages_fit"] for m in MODEL_ORDER]

    ax_r.bar([x - width for x in xs], en_pages, width, color=COL_EN,
             label="English", edgecolor="none")
    ax_r.bar(xs,                       nb_pages, width, color=COL_NB,
             label="Norsk (Bokmål)", edgecolor="none")
    ax_r.bar([x + width for x in xs], nn_pages, width, color=COL_NN,
             label="Norsk (Nynorsk)", edgecolor="none")

    for i, (en, nb, nn) in enumerate(zip(en_pages, nb_pages, nn_pages)):
        ax_r.text(i - width, en + 8, f"{en:.0f}", ha="center", fontsize=9, color=COL_INK)
        ax_r.text(i,         nb + 8, f"{nb:.0f}", ha="center", fontsize=9, color=COL_INK)
        ax_r.text(i + width, nn + 8, f"{nn:.0f}", ha="center", fontsize=9, color=COL_INK)

    ax_r.set_xticks(xs)
    ax_r.set_xticklabels([MODEL_LABEL[m] for m in MODEL_ORDER], fontsize=10)
    ax_r.set_ylabel("A4-sider med innhold (~300 ord/side)")
    ax_r.set_title("Hvor mange sider får plass i et 128K context-vindu?", fontsize=11, color=COL_INK)
    ax_r.spines["top"].set_visible(False)
    ax_r.spines["right"].set_visible(False)
    ax_r.grid(axis="y", alpha=0.25)
    ax_r.legend(loc="upper right", frameon=False, fontsize=9)
    ax_r.set_ylim(-70, max(en_pages + nb_pages + nn_pages) + 40)

    ax_r.axvspan(norm_idx - 0.45, norm_idx + 0.45, color=COL_HIGHLIGHT, alpha=0.08, zorder=0)
    # The "fix" annotation — placed below the bars, low-key, no arrow collision
    ax_r.text(
        norm_idx, -45,
        "Norsk-trent tokenizer\nreverserer skatten",
        ha="center", va="top",
        fontsize=9.5, color=COL_HIGHLIGHT, fontweight=600,
    )

    fig.suptitle(
        "DIA-TAX: Norsk koster mer å spørre KI om enn engelsk\n"
        "Måling: 200 FLORES-200-setninger, parret BM/NN/EN-innhold",
        fontsize=12, color=COL_INK, y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out = FIGURES_DIR / "tokenization_tax.png"
    fig.savefig(out, dpi=160, facecolor=COL_BG)
    plt.close(fig)
    print(f"[04] -> {out}")

    # ============================================================
    # Alt visual: the "skyline" — context windows as buildings,
    # filled with how much content actually fits.
    # ============================================================
    fig2, ax = plt.subplots(figsize=(12, 6))
    fig2.patch.set_facecolor(COL_BG)
    ax.set_facecolor(COL_BG)

    # Horizontal bar per (model, lang). Width = pages in 128K window.
    labels = []
    values = []
    colors = []
    highlight_idx = []
    i = 0
    for m in MODEL_ORDER:
        for lang, col in [("en", COL_EN), ("nb", COL_NB), ("nn", COL_NN)]:
            pages = fit[f"{m}::{lang}"]["windows"]["128K"]["pages_fit"]
            labels.append(f"{MODEL_LABEL[m]} · {lang.upper()}")
            values.append(pages)
            colors.append(col)
            if m == "normistral-7b" and lang in {"nb", "nn"}:
                highlight_idx.append(i)
            i += 1

    ys = list(range(len(labels)))
    ax.barh(ys, values, color=colors, edgecolor="none")
    for y, v in zip(ys, values):
        ax.text(v + 5, y, f"{v:.0f} sider", va="center", fontsize=9, color=COL_INK)

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("A4-sider som får plass i et 128K context-vindu (~300 ord/side)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    ax.set_xlim(0, max(values) + 70)

    ax.set_title(
        "Samme 128K context-vindu. Forskjellige språk. Forskjellig kapasitet.\n"
        "Norsk-trent tokenizer (NorMistral) reverserer regnestykket.",
        fontsize=11, color=COL_INK, loc="left",
    )

    fig2.tight_layout()
    out2 = FIGURES_DIR / "skyline.png"
    fig2.savefig(out2, dpi=160, facecolor=COL_BG)
    plt.close(fig2)
    print(f"[04] -> {out2}")


if __name__ == "__main__":
    main()
