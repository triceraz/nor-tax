"""Tokenize parallel BM/NN/NB/EN sentences across multiple tokenizers.

Reads the two parallel-pair files from DIA-LOC:
  d1_bm_nn_pairs.jsonl  — 200 sentence pairs, bm vs nn (apertium-translated
                          from Wikipedia)
  d2_nb_en_pairs.jsonl  — 200 sentence pairs, nb vs en (FLORES-200)

For each tokenizer in lib.config.TOKENIZERS, counts tokens for every
language variant in every pair and writes the result to:

  runs/tokens.jsonl  — one row per (pair_id, tokenizer, lang, text)
                       with token_count, char_count, word_count

Downstream scripts (02_aggregate, 03_plot) read this single file.

Run:
    python src/01_tokenize.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import (
    PAIRS_BM_NN,
    PAIRS_NB_EN,
    RUNS_DIR,
    TOKENIZERS,
)


def _word_count(text: str) -> int:
    """Whitespace-split word count. Crude but consistent across languages
    that use spaces. CJK/Thai handled separately if we extend later."""
    return len(text.split())


def _load_pairs(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_tokenizer(kind: str, ident: str):
    if kind == "tiktoken":
        import tiktoken
        return ("tiktoken", tiktoken.get_encoding(ident))
    if kind == "hf":
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(ident, trust_remote_code=True)
        return ("hf", tok)
    raise ValueError(f"unknown tokenizer kind: {kind}")


def _count_tokens(tok_handle, text: str) -> int:
    kind, tok = tok_handle
    if kind == "tiktoken":
        return len(tok.encode(text))
    if kind == "hf":
        # add_special_tokens=False — we want the raw byte cost of the
        # content, not template overhead.
        return len(tok.encode(text, add_special_tokens=False))
    raise ValueError(f"unknown tokenizer kind: {kind}")


def main() -> None:
    pairs_d1 = _load_pairs(PAIRS_BM_NN)
    pairs_d2 = _load_pairs(PAIRS_NB_EN)
    print(f"[01] loaded {len(pairs_d1)} bm/nn pairs, {len(pairs_d2)} nb/en pairs")

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RUNS_DIR / "tokens.jsonl"

    with out_path.open("w", encoding="utf-8") as f:
        for label, kind, ident in TOKENIZERS:
            print(f"[01] loading tokenizer: {label} ({ident}) ...")
            try:
                tok_handle = _load_tokenizer(kind, ident)
            except Exception as e:
                print(f"[01]   FAILED to load {label}: {e}")
                continue

            for pairs, lang_a, lang_b in [
                (pairs_d1, "bm", "nn"),
                (pairs_d2, "nb", "en"),
            ]:
                for row in pairs:
                    for lang_key, text_key in [(lang_a, "text_a"), (lang_b, "text_b")]:
                        text = row[text_key]
                        rec = {
                            "pair_id":     row["id"],
                            "tokenizer":   label,
                            "lang":        lang_key,
                            "char_count":  len(text),
                            "word_count":  _word_count(text),
                            "token_count": _count_tokens(tok_handle, text),
                        }
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

            print(f"[01]   {label} done")

    print(f"[01] -> {out_path}")


if __name__ == "__main__":
    main()
