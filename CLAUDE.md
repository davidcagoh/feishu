# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a quantitative trading competition project (Feishu/Lark Quant Competition). The goal is to build alpha signals or a trading strategy using the provided in-sample data. No code exists yet — this CLAUDE.md will grow as the project develops.

## Data Access Rules

- **Never read raw files directly**: `data/daily_data_in_sample.parquet` and `data/lob_data_in_sample.parquet` are too large for in-context use.
- **Always use sample files for development**: `data/daily_sample.parquet` (first 20 days) and `data/lob_sample.parquet` (D001–D003).
- **Run scripts via `!`** and paste back summary output (IC, IR, describe(), errors) rather than reading data files.
- Raw files are excluded from git via `.gitignore`. Sample files may be committed.

## Data Files

All files live in `data/`. Both datasets use opaque IDs: `asset_id` like `A000651`, `trade_day_id` like `D001`–`D484` (484 trading days, 2,270 assets).

### `data/daily_data_in_sample.parquet` — 1,060,121 rows × 10 cols
Daily OHLCV bar data per asset per day.

| Column | Type | Description |
|---|---|---|
| `asset_id` | str | Asset identifier |
| `trade_day_id` | str | Day identifier |
| `open`, `high`, `low`, `close` | float64 | Unadjusted prices |
| `volume` | float64 | Share volume |
| `amount` | float64 | Turnover (price × volume) |
| `adj_factor` | float64 | Cumulative adjustment factor for splits/dividends |
| `vwap_0930_0935` | float64 | VWAP in the first 5-minute opening window |

**Adjusted price** = `close * adj_factor` (apply consistently across history before cross-sectional comparisons).

### `data/lob_data_in_sample.parquet` — 24,810,697 rows × 43 cols
Limit order book snapshots, ~23–24 per trading day per asset (09:40–15:00).

Columns: `asset_id`, `trade_day_id`, `time`, then 10-level ask/bid prices (`ask_price_1`…`ask_price_10`, `bid_price_1`…`bid_price_10`) and 10-level ask/bid volumes (`ask_volume_1`…`ask_volume_10`, `bid_volume_1`…`bid_volume_10`). All price/volume fields are `float32`.

Level 1 is best (tightest) quote. Mid-price = `(ask_price_1 + bid_price_1) / 2`. LOB data starts at 09:40 (post-opening auction).

## Loading Data

```python
import pandas as pd

# Development — use sample files
daily = pd.read_parquet("data/daily_sample.parquet")
lob   = pd.read_parquet("data/lob_sample.parquet")

# Full run — filter early; never load LOB unfiltered
daily_full = pd.read_parquet("data/daily_data_in_sample.parquet")
lob_day = pd.read_parquet(
    "data/lob_data_in_sample.parquet",
    filters=[("trade_day_id", "==", "D001")]
)
```

## Session Start Routine

At the start of every session, automatically run these steps and report a brief status — no need to ask first:

1. **Sync wiki**: Run `git pull origin main` to pull any updates pushed by the scheduled paper-search agent (runs every Wednesday 5pm ET)
2. **Evaluate signals**: Run `python eval/run_eval.py --sample` and capture the output
3. **Health check**: Read `wiki/_index.md`. Check for new papers added by the agent, fix any obvious gaps (missing index entries, broken wikilinks), complete any open tasks marked `[ ]` that are doable now
4. **Report**: In 4–6 bullet points: what the agent added since last session, eval results summary, any open tasks worth doing today

Signal implementations live in `signals/`. Add new signals there following the existing pattern (each module exports `compute(daily, lob=None) -> pd.DataFrame`). Eval results are written to `wiki/results/`.

## Key Domain Notes

- **No calendar mapping is given** — `D001`–`D484` are ordinal, not calendar dates. Do not assume day gaps or weekends.
- **Cross-sectional neutralisation** is typical for alpha research: demean or rank signals within each `trade_day_id` before computing IC/IR.
- **Adjusted prices**: use `close * adj_factor` for return calculations spanning corporate actions.
- **LOB imbalance** is a common microstructure signal: `(bid_volume_1 - ask_volume_1) / (bid_volume_1 + ask_volume_1)`.
