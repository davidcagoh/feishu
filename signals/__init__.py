"""
Signal registry. Each module exports a compute(daily, lob=None) -> pd.DataFrame function.
Returns a (trade_day_id x asset_id) DataFrame of cross-sectionally z-scored signal values.
"""

from signals import (
    short_term_reversal,
    lob_imbalance,
    price_to_vwap,
    volume_reversal,
    ofi_matched_filter,
    ofi_ou,
    alpha191_046,
    alpha191_071,
    composite_daily,
    composite_full,
)

REGISTRY = {
    "short_term_reversal": short_term_reversal,
    "lob_imbalance": lob_imbalance,
    "price_to_vwap": price_to_vwap,
    "volume_reversal": volume_reversal,
    "ofi_matched_filter": ofi_matched_filter,
    "ofi_ou": ofi_ou,
    "alpha191_046": alpha191_046,
    "alpha191_071": alpha191_071,
    "composite_daily": composite_daily,
    "composite_full": composite_full,
}
