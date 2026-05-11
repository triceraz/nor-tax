"""Compute "how much content fits in a context window" per (tokenizer, lang).

For each tokenizer and each language, scale FLORES sentences (we have 200
pairs, median ~20 words each in EN) to standard context-window sizes:
8K, 32K, 128K, 200K.

Output (runs/context_fit.json):
  per (tokenizer, lang, window): how many FLORES sentences fit, how many
  words that translates to, how many "A4 pages" (~300 words/page).

This gives the LinkedIn-friendly framing: "128K context window holds X
words of English, Y words of Norwegian. Same content. Different limit."

Run:
    python src/03_context_window.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import CONTEXT_WINDOWS, RUNS_DIR


WORDS_PER_PAGE = 300  # standard A4 prose density


def main() -> None:
    in_path = RUNS_DIR / "tokens.jsonl"
    rows = [json.loads(line) for line in in_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    # Bucket by (tokenizer, lang). Compute total tokens, total words across
    # the FLORES sample. Then: tokens_per_word = total_tokens / total_words.
    # window_in_words = window_tokens / tokens_per_word.
    from collections import defaultdict
    bucket: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"tokens": 0, "words": 0, "chars": 0})
    for r in rows:
        b = bucket[(r["tokenizer"], r["lang"])]
        b["tokens"] += r["token_count"]
        b["words"]  += r["word_count"]
        b["chars"]  += r["char_count"]

    out = {}
    for (tok, lang), b in bucket.items():
        tpw = b["tokens"] / max(b["words"], 1)
        per_window = {}
        for wlabel, wtokens in CONTEXT_WINDOWS:
            words_fit = int(wtokens / tpw)
            pages_fit = words_fit / WORDS_PER_PAGE
            per_window[wlabel] = {
                "window_tokens": wtokens,
                "words_fit":     words_fit,
                "pages_fit":     round(pages_fit, 1),
            }
        out[f"{tok}::{lang}"] = {
            "tokenizer":       tok,
            "lang":            lang,
            "tokens_per_word": round(tpw, 3),
            "windows":         per_window,
        }

    (RUNS_DIR / "context_fit.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ---- print headline: 128K window ----
    print()
    print("words that fit in a 128K context window:")
    print(f"  {'tokenizer':<15} {'EN':>8} {'NB':>8} {'BM':>8} {'NN':>8}    NB loss")
    for tok in sorted({k.split("::")[0] for k in out.keys()}):
        en = out.get(f"{tok}::en", {}).get("windows", {}).get("128K", {}).get("words_fit", 0)
        nb = out.get(f"{tok}::nb", {}).get("windows", {}).get("128K", {}).get("words_fit", 0)
        bm = out.get(f"{tok}::bm", {}).get("windows", {}).get("128K", {}).get("words_fit", 0)
        nn = out.get(f"{tok}::nn", {}).get("windows", {}).get("128K", {}).get("words_fit", 0)
        loss = ((en - nb) / en * 100) if en else 0
        print(f"  {tok:<15} {en:>8,} {nb:>8,} {bm:>8,} {nn:>8,}    {loss:>+5.0f}%")

    print()
    print("approximate A4 pages in 128K window:")
    print(f"  {'tokenizer':<15} {'EN':>8} {'NB':>8} {'NN':>8}")
    for tok in sorted({k.split("::")[0] for k in out.keys()}):
        en = out.get(f"{tok}::en", {}).get("windows", {}).get("128K", {}).get("pages_fit", 0)
        nb = out.get(f"{tok}::nb", {}).get("windows", {}).get("128K", {}).get("pages_fit", 0)
        nn = out.get(f"{tok}::nn", {}).get("windows", {}).get("128K", {}).get("pages_fit", 0)
        print(f"  {tok:<15} {en:>8.1f} {nb:>8.1f} {nn:>8.1f}")


if __name__ == "__main__":
    main()
