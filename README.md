# Feishu Quant Competition

## Strategy

The portfolio holds the N lowest-volatility stocks (60-day rolling return std) among liquid Chinese A-shares, rebalancing daily. A volatility-managed overlay (Wang & Li 2024) sits on top: on days where the 20-day rolling market variance exceeds 3x its in-sample median, the signal is blanked and the backtest holds the previous portfolio unchanged instead of rebalancing into a turbulent market. This avoids the execution-gap problem that destroys IC-based reversal strategies — the overnight gap that drives reversal alpha has already occurred before the `vwap_0930_0935` buy window opens, leaving nothing to capture. Minimum-volatility stocks (SOEs, utilities, banks) suffer no such gap and exhibit reliable positive execution IC.

## Results (In-Sample, D001–D484)

| Strategy | CAGR | Sharpe | MDD | Score |
|---|---|---|---|---|
| `vol_managed` (submission) | +9.04% | 0.981 | 9.38% | 0.3116 |
| `low_vol` baseline | +8.81% | 0.961 | 9.38% | 0.3045 |
| Market (random N=20) | ≈ −18% | — | — | — |

Score = 0.45 × CAGR + 0.30 × Sharpe + 0.25 × (−MDD).

## Repo Structure

```
data/           — parquet files; raw files gitignored, sample files committed
signals/        — signal implementations; each exports compute(daily, lob=None) -> pd.DataFrame
eval/           — backtest engine, IC evaluator, submission generator
wiki/           — research notes, paper summaries, backtest results
submissions/    — competition CSV output (gitignored until final submission)
```

## Quick Start

```bash
pip install -r requirements.txt

# Smoke test on 20-day sample (fast)
python eval/run_eval.py --sample

# Full in-sample backtest (requires daily_data_in_sample.parquet)
python eval/backtest.py --signal vol_managed --sell-mode close --n-stocks 100
```

## OOS Submission (May 28, 2026)

When OOS data drops:

```bash
python eval/generate_submission.py --daily data/daily_data_oos.parquet
```

Verify `submissions/submission_sell_close.csv` matches the format in the competition brief (§4), then submit before June 1.

## Signal Interface

All signals live in `signals/`. Each exports:

```python
def compute(daily: pd.DataFrame, lob: pd.DataFrame = None) -> pd.DataFrame:
    ...
```

Output: a `(trade_day_id × asset_id)` DataFrame, cross-sectionally z-scored within each day. Higher value = more bullish. All-NaN rows are skipped by the backtest (no rebalance that day).

## Key Finding: IC Does Not Equal Portfolio Alpha

Every IC-based reversal signal (e.g. `volume_reversal` IR=7.72, `composite_full` IR=9.64) produces negative or near-zero CAGR in actual portfolio construction. Root cause: the reversal alpha is the overnight gap — prices move between yesterday's close and today's open before the `vwap_0930_0935` execution window. By the time the strategy can buy, the edge has been captured by whoever held overnight. See `wiki/_index.md` for the full analysis.

## Data

Two datasets, opaque IDs (`asset_id` like `A000651`, `trade_day_id` like `D001`–`D484`, 484 trading days, 2,270 assets).

- `data/daily_data_in_sample.parquet` — 1,060,121 rows × 10 cols: OHLCV, `adj_factor`, `vwap_0930_0935`
- `data/lob_data_in_sample.parquet` — 24,810,697 rows × 43 cols: 10-level ask/bid snapshots, ~23–24 per day per asset

Sample files (`daily_sample.parquet`, `lob_sample.parquet`) cover the first 20 days / D001–D003 and are safe to commit. Always develop against sample files; never load the full LOB unfiltered.

```python
import pandas as pd

daily = pd.read_parquet("data/daily_sample.parquet")   # development
lob   = pd.read_parquet("data/lob_sample.parquet")

# Full LOB — filter by day to avoid 24M-row load
lob_day = pd.read_parquet(
    "data/lob_data_in_sample.parquet",
    filters=[("trade_day_id", "==", "D001")]
)
```

Adjusted price = `close * adj_factor`. Apply consistently before any cross-sectional comparison.
