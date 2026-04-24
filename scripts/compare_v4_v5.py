"""
IS backtest comparison: trend_vol_v4 vs trend_vol_v5.

Pre-registered acceptance criterion: v5 Score within [v4 - 0.01, v4 + 0.01].
  - If v5 is within that band, accept v5 as a drop-in replacement
    (adds OOS bull-regime insurance at negligible IS cost).
  - If v5 is below the band, reject — detector too noisy on IS, stay with v4.
  - If v5 is above the band (unlikely), investigate whether v5 has
    inadvertently leaked regime info into stock selection.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.backtest import run_backtest  # noqa: E402
from signals import trend_vol_v4, trend_vol_v5  # noqa: E402


def _summarise(name: str, res: dict) -> None:
    print(
        f"{name:14s}  CAGR={res['cagr']*100:+.2f}%  "
        f"SR={res['sharpe']:+.3f}  MDD={res['mdd']*100:.2f}%  "
        f"Score={res['score']:.4f}  Days={res['n_days']}"
    )


def main() -> None:
    daily = pd.read_parquet("data/daily_data_in_sample.parquet")

    sig4 = trend_vol_v4.compute(daily, lob=None)
    w4 = trend_vol_v4.compute_weights(daily, lob=None)
    res4 = run_backtest(daily, sig4, sell_mode="open", n_stocks=20, weights=w4)

    sig5 = trend_vol_v5.compute(daily, lob=None)
    w5 = trend_vol_v5.compute_weights(daily, lob=None)
    # Use the bull upper-bound breadth; v5 itself masks to the per-day cap
    res5 = run_backtest(
        daily, sig5, sell_mode="open",
        n_stocks=trend_vol_v5.BULL_PARAMS.n_stocks, weights=w5,
    )

    print("=" * 70)
    _summarise("trend_vol_v4", res4)
    _summarise("trend_vol_v5", res5)
    print("=" * 70)

    delta = res5["score"] - res4["score"]
    band = 0.01
    verdict = (
        "ACCEPT (within ±0.01 band)" if abs(delta) <= band
        else ("INVESTIGATE — unexpectedly better" if delta > band
              else "REJECT — detector too noisy")
    )
    print(f"ΔScore = {delta:+.4f}   Verdict: {verdict}")


if __name__ == "__main__":
    main()
