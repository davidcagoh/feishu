"""
Trend-Vol v5: regime-adaptive wrapper around trend_vol_v4.

Motivation
----------
The IS period (D001–D484) is bear-dominated, so trend_vol_v4 — with its
strict low-vol selection, 35d trend filter at threshold=-0.025, and
small breadth (N=20) — is IS-optimal. The OOS period (D485–D726) is
unknown. If it turns out to be a bull regime, low-vol strategies are
known to lag (Soebhag et al. 2025; Blitz, Hanauer & van Vliet 2021;
Wang & Li 2024). v5 addresses this without fitting anything to IS:

  regime == bull   → N=30, trend_threshold=0.00 (from paper guidance, not IS sweep)
  regime != bull   → v4 defaults (N=20, threshold=-0.025, ERC weights)

The regime itself comes from `signals.regime.regime_labels`, which is
a deterministic price-only classifier (not fit to IS).

Why we don't tune the bull branch
----------------------------------
IS is overwhelmingly bear. Any parameter we pick for the bull branch by
maximising IS Score would either never fire (because bull days are rare
in IS) or would be tuned on the tiny bull window inside IS and overfit.
N=30 and threshold=0.00 are taken from:
  - idea #21 (paper-based N expansion range 30–35; we pick the low end)
  - trend_vol_v3's original threshold (0.00), which is the natural
    "no softening" baseline before we softened it for bear days.

The expected IS behaviour of v5 is therefore: within ±0.01 of v4's
Score, because the bull branch rarely fires on IS. If it drops more,
the detector is too noisy and v5 should be rejected.

Backtest plan: see `scripts/compare_v4_v5.py` (added in the same session).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from signals import regime, trend_vol_v4


@dataclass(frozen=True)
class RegimeParams:
    n_stocks: int
    trend_threshold: float


BULL_PARAMS = RegimeParams(n_stocks=30, trend_threshold=0.00)
DEFAULT_PARAMS = RegimeParams(n_stocks=20, trend_threshold=-0.025)


def _params_for(label: str) -> RegimeParams:
    return BULL_PARAMS if label == "bull" else DEFAULT_PARAMS


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 35,
) -> pd.DataFrame:
    """Regime-conditional stock selection signal.

    On each day we:
      1. Apply the regime-dependent trend threshold to the vol-managed base.
      2. Slice the result to the top-N (by base signal value) where N is
         also regime-dependent. Unselected stocks become NaN.

    Callers (backtest / generate_submission) then run their own top-N
    slice on top; using n_stocks = BULL_PARAMS.n_stocks = 30 as the upper
    bound ensures the per-day cap encoded here is respected.
    """
    labels = regime.regime_labels(daily)

    from signals import vol_managed_v2

    base_signal = vol_managed_v2.compute(daily, lob=None)

    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    adj_close_mat = df.pivot(
        index="trade_day_id", columns="asset_id", values="adj_close"
    )
    trend = adj_close_mat / adj_close_mat.shift(trend_window) - 1.0
    trend = trend.reindex(index=base_signal.index, columns=base_signal.columns)

    labels_on_sig = labels.reindex(base_signal.index).fillna("neutral")
    thresholds = labels_on_sig.map(
        lambda lbl: _params_for(lbl).trend_threshold
    ).astype(float)
    thr_mat = pd.DataFrame(
        np.broadcast_to(thresholds.values[:, None], trend.shape),
        index=trend.index,
        columns=trend.columns,
    )

    filtered = base_signal.where(trend > thr_mat, np.nan)

    # Per-day top-N slice so the regime-dependent breadth is enforced
    n_per_day = labels_on_sig.map(lambda lbl: _params_for(lbl).n_stocks).astype(int)
    out = filtered.copy()
    for day, row in filtered.iterrows():
        n = int(n_per_day.loc[day])
        valid = row.dropna()
        if len(valid) <= n:
            continue
        keep = valid.nlargest(n).index
        drop = row.index.difference(keep)
        out.loc[day, drop] = np.nan
    return out


def compute_weights(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    weight_window: int = 60,
) -> pd.DataFrame:
    """ERC weights — identical mechanics to trend_vol_v4."""
    return trend_vol_v4.compute_weights(
        daily, lob=lob, weight_window=weight_window
    )


def n_stocks_per_day(daily: pd.DataFrame) -> pd.Series:
    """Per-day N; bull days get more breadth, others get v4 default."""
    labels = regime.regime_labels(daily)
    return labels.map(lambda lbl: _params_for(lbl).n_stocks).astype(int)
