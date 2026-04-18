"""
Volatility-managed low-vol with 120-day rolling window (Signal #13).

Same as vol_managed but uses a 120-day (instead of 60-day) rolling std for
the base low_vol signal. Longer window = more stable stock rankings = lower
turnover = lower transaction costs.

Hypothesis: reduced churn at the margin of the top-N selection improves net
CAGR without changing the character of the portfolio.

All other parameters (vol_managed overlay window, sigma_threshold) unchanged.
"""

import pandas as pd

from signals import vol_managed


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    window: int = 20,
    sigma_threshold: float = 3.0,
    excl_illiq: float = 0.05,
) -> pd.DataFrame:
    return vol_managed.compute(
        daily,
        lob=lob,
        window=window,
        sigma_threshold=sigma_threshold,
        base_window=120,
        excl_illiq=excl_illiq,
    )
