"""Shared config for DIA-TAX (Norwegian tokenization tax)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
RUNS_DIR = REPO_ROOT / "runs"
FIGURES_DIR = REPO_ROOT / "paper" / "figures"

# Parallel pair sources from DIA-LOC. We reuse them directly.
DIA_LOC_DATA = REPO_ROOT.parent / "dia-loc" / "data"
PAIRS_BM_NN = DIA_LOC_DATA / "d1_bm_nn_pairs.jsonl"   # 200 pairs, bm vs nn
PAIRS_NB_EN = DIA_LOC_DATA / "d2_nb_en_pairs.jsonl"   # 200 pairs, nb vs en (FLORES-200)

# Tokenizer list. Each tuple is (label, kind, identifier).
# kind: "tiktoken" for OpenAI, "hf" for HuggingFace AutoTokenizer.
TOKENIZERS: list[tuple[str, str, str]] = [
    ("gpt-4o",        "tiktoken", "o200k_base"),
    ("gpt-4-legacy",  "tiktoken", "cl100k_base"),
    ("gemma-3-4b",    "hf",       "google/gemma-3-4b-it"),
    ("qwen-2.5-1.5b", "hf",       "Qwen/Qwen2.5-1.5B-Instruct"),
    ("normistral-7b", "hf",       "norallm/normistral-7b-warm"),
]

# Context window sizes (in tokens) we report against.
CONTEXT_WINDOWS: list[tuple[str, int]] = [
    ("8K",    8_192),
    ("32K",   32_768),
    ("128K",  131_072),
    ("200K",  200_000),
]
