# Factoring in the Low-Volatility Factor

**Authors:** Amar Soebhag, Guido Baltussen, Pim van Vliet
**Venue/Source:** SSRN Working Paper
**arXiv/DOI:** SSRN:5295002
**Date:** June 2025

---

## Core Claim
The low-volatility factor is absent from standard asset pricing models because of an asymmetry between its two legs: the long leg (long low-vol stocks, market-beta-hedged) delivers genuine alpha that survives transaction costs, while the short leg (short high-vol stocks, market-beta-hedged) does not. Adding low-vol as a standalone factor to Fama-French-style models improves Sharpe ratios by 13–17%.

---

## Method
U.S. equity data 1972–2023. Construct hedged long-leg and hedged short-leg portfolios separately, neutralising market beta on each side. Test whether each leg adds alpha after full five-factor Fama-French adjustment. Efficient frontier analysis allocates ~26–29% weight to the hedged long leg in mean-variance optimal portfolios. Robustness across different low-risk measures (volatility, beta, idiosyncratic vol) and sub-periods. Factor alpha tested in-sample and out-of-sample.

---

## Results
- Adding low-vol factor improves Sharpe in standard models by **13–17%** across methodological variants
- Efficient portfolios assign **~26–29% weight** to the hedged long leg
- Long leg: alpha **significant and cost-robust** across all test periods
- Short leg: alpha marginal after transaction costs — explains why standard models exclude the combined long-short factor
- Bull-market periods are the primary performance drag on low-vol strategies; the long leg still delivers positive risk-adjusted returns in bull markets but underperforms the market index

---

## Implementable Idea
**For our long-only strategy, this paper has two direct implications:**

1. **Structural validation** — Our long-only constraint means we *already* implement only the alpha-generating long leg. We are doing the right thing: the paper confirms that the long-only low-vol premium is genuine and cost-robust.

2. **Bull-regime N expansion** — In bull markets (low cross-sectional volatility), the long leg underperforms the market because its defensive character reduces beta exposure. The natural fix in a long-only context is to expand N (hold more stocks) during detected bull regimes to restore beta exposure without shorting:

```python
# Dynamic N: expand universe when market vol is calm (bull regime proxy)
market_vol_22d = market_ret.rolling(22).std() * np.sqrt(252)
long_run_median_vol = market_vol_22d.rolling(120).median()

# Bull regime: market vol well below historical median
if market_vol_22d.iloc[-1] < 0.75 * long_run_median_vol.iloc[-1]:
    N = 35  # expand universe, capture more beta in bull market
else:
    N = 20  # normal/bear: concentrate in lowest-vol as per trend_vol_v4
```

**Addresses priority:** Priority 1 (bull-market resilience — confirms low-vol long leg is structurally sound; bull underperformance addressable by relaxing N in calm regimes). Also Priority 3 (stock selection within low-vol — the quality interaction is implicit: low-vol long leg naturally excludes distressed high-vol stocks).

---

## Relevance to Feishu Competition
Our IS period (D001–D484) is a bear market. The paper confirms trend_vol_v4 (long-only low-vol) is the theoretically correct implementation of the low-vol premium. The primary OOS risk is a bull market: Chinese A-shares entered a "slow bull" in 2025, and D485–D726 may be primarily bull. The paper's key reassurance is that the long leg does not *lose* in bull markets — it merely underperforms the index. The practical hedge is dynamic N expansion when a bull regime is detected before or during the OOS period. This should be tested on IS as a sensitivity check before May 28.

---

## Concepts
-> [[factor-models]] | [[chinese-ashore-market]] | [[kelly-betting]]
