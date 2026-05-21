"""
Trend-Vol v6: regime-conditional threshold at fixed breadth N=20.

Hypothesis
----------
v5 (`trend_vol_v5.py`) adapts BOTH the trend threshold AND the breadth N
on bull days. v6 isolates the threshold effect by keeping N=20 fixed
across regimes:

    regime == bull   → trend_threshold=0.00, N=20
    regime != bull   → trend_threshold=-0.025, N=20  (== v4 defaults)

Origin and pre-registration
---------------------------
See `wiki/decisions/001-kill-criteria-trend-vol-v6.md`. The hypothesis
arose from a driver bug (eval_layers.py applied n_stocks=20 to v5
unintentionally) and the resulting hybrid outscored v4 by +0.019 in IS.
This module isolates that perturbation in a deliberately-named strategy
so it can be evaluated against a pre-registered acceptance protocol.

Status
------
**SHELVED 2026-05-20** — pre-registered validation in
`scripts/validate_trend_vol_v6.py` showed tuning ΔScore +0.0305 but
held-out ΔScore −0.0475. The IS signal did not survive the D401–D484
held-out window. See `wiki/results/2026-05-20-trend-vol-v6-validation.md`.

Module retained for reproducibility; do not deploy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from signals import regime, trend_vol_v4


N_STOCKS = 20  # module attribute consumed by scripts/eval_layers.py


@dataclass(frozen=True)
class RegimeParams:
    n_stocks: int
    trend_threshold: float


BULL_PARAMS = RegimeParams(n_stocks=20, trend_threshold=0.00)
DEFAULT_PARAMS = RegimeParams(n_stocks=20, trend_threshold=-0.025)


def _params_for(label: str) -> RegimeParams:
    return BULL_PARAMS if label == "bull" else DEFAULT_PARAMS


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 35,
) -> pd.DataFrame:
    """Regime-conditional trend filter at fixed N=20.

    Structure is identical to trend_vol_v5.compute(...) except both regime
    branches use N=20; the only conditional behaviour is the trend threshold.
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

    # Per-day top-N slice — fixed at 20 across regimes
    out = filtered.copy()
    for day, row in filtered.iterrows():
        n = int(_params_for(labels_on_sig.loc[day]).n_stocks)
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
    """ERC weights — identical to trend_vol_v4."""
    return trend_vol_v4.compute_weights(
        daily, lob=lob, weight_window=weight_window
    )
