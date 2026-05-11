# DIA-TAX

**The Norwegian Tokenization Tax: How BPE Penalizes Norwegian Speakers and What a Norwegian-Trained Tokenizer Recovers.**

Third paper in the DIA-* series after [DIA-LOC](https://github.com/triceraz/dia-loc) (where the dialect signal lives in Qwen 2.5) and [DIA-INT](https://github.com/triceraz/dia-int) (where to intervene with LoRA).

## TL;DR

We measured tokens-per-word for 200 parallel English/Bokmål/Nynorsk sentences from FLORES-200 + Wikipedia, across four tokenizers Tenki actually uses or considers:

| Tokenizer | EN | NB | BM | NN | NB/EN |
|---|---:|---:|---:|---:|---:|
| GPT-4o (o200k_base) | 1.22 | 1.69 | 2.00 | 2.00 | **1.38x** |
| GPT-4 (cl100k_base) | 1.23 | 2.00 | 2.24 | 2.33 | **1.62x** |
| Qwen 2.5 1.5B | 1.26 | 2.02 | 2.37 | 2.43 | **1.60x** |
| NorMistral 7B | 1.73 | 1.46 | 1.92 | 2.00 | **0.84x** |

Translated to context-window capacity (128K tokens):

| Tokenizer | EN pages | NB pages | NB loss |
|---|---:|---:|---:|
| GPT-4o | 348 | 256 | **-27%** |
| GPT-4 | 347 | 222 | **-36%** |
| Qwen 2.5 | 337 | 218 | **-35%** |
| NorMistral 7B | 249 | 295 | **+18%** |

Two findings:

1. **English-trained tokenizers tax Norwegian by 27–36% in usable context.** Same content. Same model. Smaller effective window.
2. **A Norwegian-trained tokenizer (NorMistral) reverses the tax.** Norwegian becomes cheaper than English on a Norwegian corpus.

Bokmål vs Nynorsk is a near-wash: the tax is on "being Norwegian," not on dialect choice.

## Reproducing

Requires the [DIA-LOC](https://github.com/triceraz/dia-loc) parallel-pair files at `../dia-loc/data/d1_bm_nn_pairs.jsonl` and `d2_nb_en_pairs.jsonl`.

```bash
python -m venv .venv
.venv\Scripts\activate              # Windows
pip install tiktoken transformers matplotlib

python src/01_tokenize.py           # ~30s, cached after first run
python src/02_aggregate.py          # prints summary table
python src/03_context_window.py     # prints context-fit table
python src/04_plot.py               # writes paper/figures/*.png
```

Outputs:

- `runs/tokens.jsonl` — per-pair token counts
- `runs/summary_per_lang.json` — aggregate stats per (tokenizer, lang)
- `runs/summary_paired.json` — paired ratios (NB/EN, NN/BM)
- `runs/context_fit.json` — pages that fit per (tokenizer, lang, window)
- `paper/figures/tokenization_tax.png` — main two-panel figure
- `paper/figures/skyline.png` — LinkedIn-format horizontal-bar figure

## Author

Andreas Grønbeck (Tenki Labs AS).
