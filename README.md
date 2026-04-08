# Feishu Quant Competition

Alpha signal research for the Feishu/Lark Quant Competition. The goal is to build predictive signals on Chinese A-share data (daily OHLCV + limit order book snapshots).

## Repo Structure

```
feishu/
├── data/                          # Competition data (gitignored except samples)
│   ├── daily_sample.parquet       # First 20 days, safe to commit
│   ├── lob_sample.parquet         # D001–D003 LOB, safe to commit
│   ├── daily_data_in_sample.parquet   # Full daily (484 days × 2270 assets) — local only
│   ├── lob_data_in_sample.parquet     # Full LOB (24.8M rows) — local only
│   └── create_sample.py           # Script that generated the sample files
│
├── signals/                       # Signal implementations
│   ├── __init__.py                # Registry — add new signals here
│   ├── short_term_reversal.py
│   ├── lob_imbalance.py
│   ├── price_to_vwap.py
│   └── volume_reversal.py
│
├── eval/
│   └── run_eval.py                # Evaluate all signals → wiki/results/
│
├── strategy_papers/               # Raw PDFs of reference papers
│
├── wiki/                          # Research knowledge base (auto-maintained)
│   ├── _index.md                  # Master index — start here
│   ├── papers/                    # One .md summary per paper
│   ├── concepts/                  # Topic articles (factor models, LOB, etc.)
│   ├── ideas/                     # Concrete signal ideas for the competition
│   ├── results/                   # Eval output — latest.md updated each session
│   └── logs/                      # Agent activity logs
│
├── Feishu_Quant_Competition.pdf   # Competition brief
└── CLAUDE.md                      # Instructions for Claude Code
```

## Getting Started

### 1. Install dependencies

```bash
pip install pandas numpy scipy pyarrow pypdf
```

### 2. Get the data

The full parquet files are not in the repo (too large, competition data). You need:
- `data/daily_data_in_sample.parquet`
- `data/lob_data_in_sample.parquet`

Once you have them, generate sample files for development:

```bash
cd data
python create_sample.py
```

### 3. Run the signal evaluator

```bash
# Fast: sample data only (20 days, smoke test)
python eval/run_eval.py --sample

# Full: all 484 days (takes a few minutes)
python eval/run_eval.py

# Single signal
python eval/run_eval.py --sample --signal short_term_reversal
```

Results are written to `wiki/results/latest.md`.

## The Data

Two datasets, both using opaque IDs (`asset_id` like `A000651`, `trade_day_id` like `D001`–`D484`).

**Daily** (`daily_data_in_sample.parquet`) — 1,060,121 rows × 10 cols:

| Column | Description |
|--------|-------------|
| `open`, `high`, `low`, `close` | Unadjusted prices |
| `volume` | Share volume |
| `amount` | Turnover (price × volume) |
| `adj_factor` | Cumulative adjustment factor for splits/dividends |
| `vwap_0930_0935` | VWAP in the first 5-min opening window (09:30–09:35) |

Always compute adjusted prices as `close * adj_factor` before cross-sectional work.

**LOB** (`lob_data_in_sample.parquet`) — 24,810,697 rows × 43 cols:  
10-level ask/bid prices and volumes, ~23–24 snapshots per day per asset, from 09:40 to 15:00.

```python
import pandas as pd

# Always use sample files during development
daily = pd.read_parquet("data/daily_sample.parquet")
lob   = pd.read_parquet("data/lob_sample.parquet")

# Full data — filter LOB early, never load it unfiltered
daily_full = pd.read_parquet("data/daily_data_in_sample.parquet")
lob_day = pd.read_parquet(
    "data/lob_data_in_sample.parquet",
    filters=[("trade_day_id", "==", "D001")]
)
```

## China-Specific Notes

This is Chinese A-share data. Key constraints vs US data:

- **T+1 settlement**: can't sell what you bought same day. Signal → next-day return is the natural evaluation horizon.
- **±10% daily price limits**: stocks hitting the limit are uninvestable. The eval script masks these automatically.
- **Short selling**: heavily restricted. Treat signals as long-biased unless otherwise specified.
- **Retail dominance**: ~85% of volume is retail. Contrarian signals (reversal, volume surprise) tend to be stronger than in US markets.

## Implementing a New Signal

1. Create `signals/your_signal.py`:

```python
import numpy as np
import pandas as pd

def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Returns a (trade_day_id × asset_id) DataFrame of signal values,
    cross-sectionally z-scored within each day.
    Positive = long, negative = short.
    """
    # ... your logic here
    return signal
```

2. Register it in `signals/__init__.py`:

```python
from signals import your_signal

REGISTRY = {
    ...
    "your_signal": your_signal,
}
```

3. Run eval to see IC/IR:

```bash
python eval/run_eval.py --sample --signal your_signal
```

## The Wiki

`wiki/` is a research knowledge base maintained by Claude Code. It summarises papers, defines concepts, and tracks signal ideas. **Don't edit it directly** — Claude maintains it.

Start at [`wiki/_index.md`](wiki/_index.md) for an overview of everything indexed so far.

A scheduled agent runs every Wednesday at 5pm ET, searches for new relevant papers, and pushes summaries to `wiki/papers/`. Results show up after a `git pull`.

## Evaluating Signals

The key metric is **IC (Information Coefficient)** — the Spearman correlation between the signal on day `t` and the cross-sectional return on day `t+1`.

| Metric | Target | Notes |
|--------|--------|-------|
| Mean IC | > 0.02 | Weak but tradeable at daily frequency |
| IR (annualised) | > 0.5 | IC mean / IC std × √252 |
| Hit rate | > 55% | % of days with positive IC |

```python
# Quick IC check for a new signal (without the eval script)
from scipy.stats import spearmanr
import pandas as pd

# signal and next_day_returns: both (day × asset) DataFrames, already z-scored
daily_ic = signal.shift(1).corrwith(next_day_returns, axis=1, method="spearman")
print(f"Mean IC: {daily_ic.mean():.4f}  IR: {daily_ic.mean() / daily_ic.std() * (252**0.5):.2f}")
```

## Current Signal Results (sample data — indicative only)

| Signal | Mean IC | IR | Notes |
|--------|---------|-----|-------|
| `volume_reversal` | 0.062 | 7.7 | High volume → reversal next day |
| `short_term_reversal` | 0.022 | 3.2 | Daily cross-sectional return reversal |
| `price_to_vwap` | -0.006 | -0.8 | Weak; may need tuning |
| `lob_imbalance` | 0.016 | — | Only 1 eval day in sample; needs full data |

_Run `python eval/run_eval.py` on full data for reliable numbers._
