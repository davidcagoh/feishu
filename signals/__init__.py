"""
Signal registry. Each module exports a compute(daily, lob=None) -> pd.DataFrame function.
Returns a (trade_day_id x asset_id) DataFrame of cross-sectionally z-scored signal values.
"""

from signals import short_term_reversal, lob_imbalance, price_to_vwap, volume_reversal

REGISTRY = {
    "short_term_reversal": short_term_reversal,
    "lob_imbalance": lob_imbalance,
    "price_to_vwap": price_to_vwap,
    "volume_reversal": volume_reversal,
}
