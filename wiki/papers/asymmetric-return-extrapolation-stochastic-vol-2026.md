# Asymmetric Nonlinear Return Extrapolation and Optimal Portfolio Choice under Stochastic Volatility

**Authors:** Dong Yan, Wenrui Ye, Zhiyue Zong, Wenting Chen (School of Statistics, University of International Business and Economics, Beijing; Department of Business, Jiangnan University, Wuxi)  
**Venue/Source:** arXiv q-fin.PM  
**arXiv/DOI:** arXiv:2606.10805  
**Date:** June 9, 2026

---

## Core Claim
Retail investors extrapolate past returns in a nonlinear, asymmetric way — saturating at extremes and responding more strongly to gains than losses. Under Heston stochastic volatility, the optimal portfolio decomposes into sentiment-distorted myopic demand, variance hedging demand, and sentiment hedging demand, generating four empirically documented anomalies including excess trading and asymmetric responses.

---

## Method
- Extends the linear extrapolation model (Barberis et al., 2015; Greenwood & Shleifer, 2014) with two modifications: (1) saturation in belief updating — responses attenuate at extreme past returns; (2) asymmetry — investors extrapolate recent gains more aggressively than recent losses
- Introduces a smooth, nonlinear, asymmetric extrapolation function (S-shaped for gains, flatter for losses)
- Solves for optimal portfolio choice of a CRRA investor under Heston (1993) stochastic volatility in closed form
- Optimal weight = (sentiment-distorted myopic demand) + (variance hedging demand) + (sentiment hedging demand)
- Calibrated against Chinese A-share cross-sectional return patterns; authors affiliated with Beijing/Jiangnan universities

---

## Results
The model generates four investor-level behavioral anomalies consistent with documented Chinese A-share patterns:

1. **Asymmetric responses**: Investors overreact to recent gains (above-linear extrapolation), underreact to recent losses (saturation)
2. **Attenuated reactions at extremes**: Very large gains/losses produce diminishing marginal belief updates
3. **Excess trading volume**: Sentiment-distorted demand creates non-fundamental turnover spikes after return streaks
4. **Welfare loss**: Misoptimised portfolio — welfare loss rises monotonically with the strength of extrapolation bias

---

## Implementable Idea
Asymmetric trend filter for stock selection: because retail investors extrapolate gains more strongly than losses, stocks with recent gains face higher reversal risk than stocks with flat-to-slightly-negative returns. Our current trend threshold is symmetric at −0.025 for all stocks. An asymmetric implementation applies a stricter upper bound to exclude recent winners (high extrapolation zone → correction risk) while using a looser lower bound to include moderate losers (saturation zone → mean-reversion likely).

```python
def asymmetric_trend_filter(trend_35d):
    """
    Asymmetric variant of the current symmetric trend filter (threshold=-0.025).
    Source: Yan et al. (arXiv:2606.10805) — asymmetric extrapolation model.

    Logic:
    - Stocks with trend > thresh_up: retail extrapolation at full strength → exclude (correction risk)
    - Stocks with trend < thresh_down: deep decliners → exclude (fundamental deterioration)
    - Middle band [thresh_down, thresh_up]: in saturation zone for losses + modest gain zone → include

    vs current: single threshold=-0.025 allows both recent gainers and modest losers equally.
    """
    thresh_up = 0.00    # stricter: exclude positive-trend stocks (retail chasing them)
    thresh_down = -0.05  # looser: allow up to -5% 35d drift (saturation zone for losses)
    return (trend_35d >= thresh_down) & (trend_35d <= thresh_up)

# In trend_vol_v4 selection:
# Replace: eligible = eligible[eligible['trend_35d'] >= -0.025]
# With: eligible = eligible[asymmetric_trend_filter(eligible['trend_35d'])]
```

Signal #32 (post-competition refinement). Note: Current symmetric filter at −0.025 already implicitly captures this asymmetry partially (allows mild losers, excludes strong decliners), but the upper bound threshold (currently unlimited → all gainers included) is the gap the asymmetric model identifies.

**Addresses priority:** Priority 3 (stock selection within low-vol universe). Provides behavioral mechanism for why our trend filter works in the Chinese A-share context, and suggests a concrete improvement: adding an upper bound to the trend filter to exclude retail-chased recent winners.

---

## Relevance to Feishu Competition
Our trend filter is a negative screen (exclude declining stocks), but it currently has no upper bound — it would include stocks trending strongly upward. This paper identifies those stocks as highest-risk for extrapolation-driven correction: retail investors accumulate them aggressively (excess trading volume anomaly), driving prices above fundamental value, then revert when the streak ends. Adding `trend_35d <= 0.00` as a soft upper cap (or `<= 0.01`) would exclude the most retail-crowded winners from our low-vol basket. Particularly relevant in bull regimes (OOS period) where extrapolation biases are stronger (more recent streaks to extrapolate). For the shortlist research report: explains the behavioral microstructure foundation of our trend-threshold design.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]]
