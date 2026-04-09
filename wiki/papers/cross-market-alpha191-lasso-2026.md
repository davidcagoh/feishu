# Cross-Market Alpha: Testing Short-Term Trading Factors in the U.S. Market via Double-Selection LASSO

**Authors:** (arXiv:2601.06499 — authors not publicly disclosed in preprint header)  
**Venue/Source:** arXiv q-fin.PM  
**arXiv/DOI:** arXiv:2601.06499  
**Date:** January 10, 2026

---

## Core Claim

Of the 191 short-term trading factors from the Chinese Alpha191 library — originally designed for A-share market microstructure — 17 survive a rigorous double-selection LASSO screen and show statistically significant incremental explanatory power for the cross-section of U.S. stock returns, even after controlling for 151 established U.S. fundamental factors. The most robust survivors are mean-reversion and deviation-from-trend factors.

---

## Method

The Alpha191 library contains 191 formulaic alpha factors developed for Chinese equities (short-horizon price/volume signals: momentum, reversal, volume patterns, intraday features). The paper:

1. Excludes 23 of 191 factors with unstable or unreliable time series → **168 factors** tested.
2. Applies **double-selection LASSO** (Belloni et al.) to screen factors robustly while controlling for a 151-factor U.S. fundamental zoo.
3. Validates the selected factors against Elastic Net and PCA benchmarks to confirm robustness.

The double-selection LASSO approach avoids the omitted-variable bias that plagues naive sequential screening in high-dimensional factor evaluation.

---

## Results

- **17 Alpha191 factors** exhibit significant incremental explanatory power (5% level) for U.S. cross-sectional returns after controlling for 151 fundamental factors.
- Most robust survivors:
  - **Factor 046 — Multi-Period Mean Reversion Ratio**: ratio of current price position within N-day high/low range; high ratio (near rolling high) predicts negative next-period return.
  - **Factor 071 — 24-Day Percentage Deviation from Mean**: deviation of price from its 24-day moving average; above-average prices revert.
- Results are confirmed across Elastic Net and PCA benchmarks.
- Cross-market validity implies these factors capture **universal microstructure patterns**, not China-specific regulatory artefacts.

---

## Relevance to Feishu Competition

These two key factors are directly implementable with the daily Feishu data and should be strong in China's market (where they were designed), given they survive even in the informationally-efficient US market.

```python
import pandas as pd
import numpy as np

daily['adj_close'] = daily['close'] * daily['adj_factor']

# ── Factor 046: Multi-Period Mean Reversion Ratio ──────────────────────────
# Rolling 20-day high and low per asset
daily['roll_max_20'] = daily.groupby('asset_id')['adj_close'].transform(
    lambda x: x.rolling(20).max()
)
daily['roll_min_20'] = daily.groupby('asset_id')['adj_close'].transform(
    lambda x: x.rolling(20).min()
)
# Position in range [0, 1]; 1 = at 20d high, 0 = at 20d low
daily['f046'] = (
    (daily['adj_close'] - daily['roll_min_20']) /
    (daily['roll_max_20'] - daily['roll_min_20'] + 1e-8)
)
# Alpha signal: negate (high position → expect reversion)
daily['alpha_046'] = daily.groupby('trade_day_id')['f046'].transform(
    lambda x: -(x - x.mean()) / (x.std() + 1e-8)
)

# ── Factor 071: 24-Day Percentage Deviation from Mean ─────────────────────
daily['sma_24'] = daily.groupby('asset_id')['adj_close'].transform(
    lambda x: x.rolling(24).mean()
)
daily['f071'] = (daily['adj_close'] - daily['sma_24']) / (daily['sma_24'] + 1e-8)
# Alpha signal: negate (above mean → expect reversion to mean)
daily['alpha_071'] = daily.groupby('trade_day_id')['f071'].transform(
    lambda x: -(x - x.mean()) / (x.std() + 1e-8)
)

# Composite: simple average of both (both are mean-reversion signals)
daily['alpha_composite'] = (daily['alpha_046'] + daily['alpha_071']) / 2
```

**Key takeaway for Feishu:** Both survivors are **mean-reversion signals**, consistent with the well-documented short-term reversal effect in Chinese equities (see [[chinese-ashore-market]]). They go beyond the simple 1-day reversal (Signal #3) by anchoring to a multi-period range (f046) or a moving average (f071), which reduces noise from single-day price jumps. This is a drop-in enhancement to Tier 1 signals.

---

## Concepts
→ [[statistical-arbitrage]] | [[mean-reversion]] | [[factor-models]] | [[chinese-ashore-market]]
