"""Aggregate token counts from runs/tokens.jsonl into summary stats.

Computes per (tokenizer, lang):
  - median tokens
  - median chars
  - median words
  - median tokens-per-word
  - median tokens-per-char
  - tokens-per-word IQR (25th-75th percentile)

And per (tokenizer, source_pair):
  - paired ratio (tokens_b / tokens_a) — same content, different language

Writes:
  runs/summary_per_lang.json    — flat stats per (tokenizer, lang)
  runs/summary_paired.json      — paired (bm vs nn, nb vs en) ratios

Plus prints a human-readable table to stdout.

Run:
    python src/02_aggregate.py
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import RUNS_DIR, TOKENIZERS


def _median(xs: list[float]) -> float:
    return statistics.median(xs) if xs else 0.0


def _percentile(xs: list[float], p: float) -> float:
    if not xs:
        return 0.0
    xs_sorted = sorted(xs)
    k = (len(xs_sorted) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(xs_sorted) - 1)
    return xs_sorted[lo] + (xs_sorted[hi] - xs_sorted[lo]) * (k - lo)


def main() -> None:
    in_path = RUNS_DIR / "tokens.jsonl"
    rows = [json.loads(line) for line in in_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"[02] loaded {len(rows)} token rows")

    # ---- per (tokenizer, lang) ----
    per_key: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        per_key[(r["tokenizer"], r["lang"])].append(r)

    summary_per_lang = {}
    for (tok, lang), recs in per_key.items():
        tpws = [r["token_count"] / max(r["word_count"], 1) for r in recs]
        tpcs = [r["token_count"] / max(r["char_count"], 1) for r in recs]
        summary_per_lang[f"{tok}::{lang}"] = {
            "tokenizer":              tok,
            "lang":                   lang,
            "n":                      len(recs),
            "tokens_median":          _median([r["token_count"] for r in recs]),
            "words_median":           _median([r["word_count"]  for r in recs]),
            "chars_median":           _median([r["char_count"]  for r in recs]),
            "tokens_per_word_median": _median(tpws),
            "tokens_per_word_p25":    _percentile(tpws, 25),
            "tokens_per_word_p75":    _percentile(tpws, 75),
            "tokens_per_char_median": _median(tpcs),
        }

    (RUNS_DIR / "summary_per_lang.json").write_text(
        json.dumps(summary_per_lang, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ---- paired ratios ----
    # For each pair_id, group rows by tokenizer + the two langs in the pair.
    # bm/nn pairs (d1_*) and nb/en pairs (d2_*) are distinguishable by id prefix.
    paired_d1: dict[str, list[tuple[int, int]]] = defaultdict(list)  # bm_tokens, nn_tokens
    paired_d2: dict[str, list[tuple[int, int]]] = defaultdict(list)  # nb_tokens, en_tokens

    rows_by_pair: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    for r in rows:
        rows_by_pair[(r["tokenizer"], r["pair_id"])][r["lang"]] = r["token_count"]

    for (tok, pid), counts in rows_by_pair.items():
        if pid.startswith("d1_") and "bm" in counts and "nn" in counts:
            paired_d1[tok].append((counts["bm"], counts["nn"]))
        if pid.startswith("d2_") and "nb" in counts and "en" in counts:
            paired_d2[tok].append((counts["nb"], counts["en"]))

    summary_paired = {}
    for tok in sorted(set(paired_d1) | set(paired_d2)):
        d1 = paired_d1.get(tok, [])
        d2 = paired_d2.get(tok, [])
        nn_over_bm = [nn / max(bm, 1) for bm, nn in d1]
        nb_over_en = [nb / max(en, 1) for nb, en in d2]
        summary_paired[tok] = {
            "n_bm_nn_pairs":      len(d1),
            "n_nb_en_pairs":      len(d2),
            "nn_tokens_per_bm":   _median(nn_over_bm),
            "nb_tokens_per_en":   _median(nb_over_en),
            "nn_p25":             _percentile(nn_over_bm, 25),
            "nn_p75":             _percentile(nn_over_bm, 75),
            "nb_p25":             _percentile(nb_over_en, 25),
            "nb_p75":             _percentile(nb_over_en, 75),
        }

    (RUNS_DIR / "summary_paired.json").write_text(
        json.dumps(summary_paired, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ---- print headline table ----
    print()
    print("tokens-per-word median (lower = more efficient)")
    print(f"  {'tokenizer':<15} {'EN':>6} {'NB':>6} {'BM':>6} {'NN':>6}   NB/EN  NN/BM")
    for label, _, _ in TOKENIZERS:
        en = summary_per_lang.get(f"{label}::en", {}).get("tokens_per_word_median")
        nb = summary_per_lang.get(f"{label}::nb", {}).get("tokens_per_word_median")
        bm = summary_per_lang.get(f"{label}::bm", {}).get("tokens_per_word_median")
        nn = summary_per_lang.get(f"{label}::nn", {}).get("tokens_per_word_median")
        if en is None:
            continue
        nb_en = (nb / en) if (nb and en) else 0
        nn_bm = (nn / bm) if (nn and bm) else 0
        print(f"  {label:<15} {en:>6.2f} {nb:>6.2f} {bm:>6.2f} {nn:>6.2f}   {nb_en:>5.2f}  {nn_bm:>5.2f}")

    print()
    print("paired nb/en ratio median (NB tokens per 1 EN token, same content):")
    for tok, s in summary_paired.items():
        print(f"  {tok:<15} {s['nb_tokens_per_en']:.2f}x  (NN/BM: {s['nn_tokens_per_bm']:.2f}x)")


if __name__ == "__main__":
    main()
