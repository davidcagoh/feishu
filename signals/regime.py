"""
Market-regime detector (price-only, deterministic, no fitting).

Used as an OOS contingency overlay for trend_vol_v5: when the competition
OOS period (D485–D726) turns out to be a bull regime, low-vol strategies
are known to underperform (Soebhag et al. 2025, Wang & Li 2024). This
detector provides a coarse bull/neutral/stress label that trend_vol_v5
consumes to decide whether to relax its trend filter and expand breadth.

Design constraint: the detector MUST NOT be fit to IS. Its thresholds
(0.75× and 1.50× the long-run median of rolling vol) come from idea #22
in the wiki, which in turn is derived from Shu & Mulvey (JPM 2025) and
the Wasserstein HMM literature. We deliberately avoid any IS-tuned
threshold sweep.

Method:
  1. Build the equal-weighted market return series from daily close×adj_factor.
  2. Compute 22-day rolling std of market returns (short-horizon vol).
  3. Compute 120-day rolling median of the above (long-run reference).
  4. Label per-day:
        bull    if vol_22d < 0.75 × median
        stress  if vol_22d > 1.50 × median
        neutral otherwise
  5. Warmup days (fewer than ~142 observations) receive 'neutral'.

Output can be queried per-day via `regime_labels(daily)` (returns a Series
indexed by trade_day_id) or scalar via `detect_regime(daily, as_of_day)`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RegimeLabel = str  # "bull" | "neutral" | "stress"

VOL_WINDOW: int = 22
MEDIAN_WINDOW: int = 120
BULL_RATIO: float = 0.75
STRESS_RATIO: float = 1.50


def _market_return_series(daily: pd.DataFrame) -> pd.Series:
    """Equal-weighted cross-sectional mean daily return from adjusted close."""
    df = daily[["asset_id", "trade_day_id", "close", "adj_factor"]].copy()
    df["adj_close"] = df["close"] * df["adj_factor"]
    wide = df.pivot(index="trade_day_id", columns="asset_id", values="adj_close")
    wide = wide.sort_index()
    rets = wide.pct_change(fill_method=None)
    market_ret = rets.mean(axis=1)
    return market_ret


def regime_labels(daily: pd.DataFrame) -> pd.Series:
    """Compute a regime label for every trade_day_id in `daily`."""
    market_ret = _market_return_series(daily)
    vol_s = market_ret.rolling(VOL_WINDOW, min_periods=VOL_WINDOW).std()
    median_s = vol_s.rolling(MEDIAN_WINDOW, min_periods=MEDIAN_WINDOW).median()

    labels = pd.Series("neutral", index=market_ret.index, dtype=object)
    ratio = vol_s / median_s
    labels[ratio < BULL_RATIO] = "bull"
    labels[ratio > STRESS_RATIO] = "stress"
    # Warmup: where we couldn't compute a median yet, stay neutral
    labels[median_s.isna()] = "neutral"
    return labels


def detect_regime(daily: pd.DataFrame, as_of_day: str) -> RegimeLabel:
    """Return the regime label for a specific trade_day_id."""
    labels = regime_labels(daily)
    if as_of_day not in labels.index:
        return "neutral"
    return str(labels.loc[as_of_day])
