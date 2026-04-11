# Portfolio Concentration Analysis — low_vol signal

_Generated: 2026-04-11_

## Methodology

Signal: `signals/low_vol.py` — selects the 100 lowest-volatility stocks each day using a 60-day rolling standard deviation of adjusted close returns, excluding the bottom 5% by 20-day rolling mean `amount` (liquidity filter). Asset IDs are opaque; no sector labels are available.

Analysis steps:
1. Ran `compute()` on the full 484-day dataset (2,270 assets, 5 columns loaded).
2. Extracted the top-100 portfolio membership for each valid day (D061–D484; first 60 days are warmup).
3. Counted per-asset selection frequency across all 424 valid portfolio days.
4. Computed daily turnover as the fraction of the 100-stock portfolio that changed vs. the prior day.
5. For correlation clustering: computed daily adj-close returns for the top-99 most-frequent assets over all 484 days, dropped assets with >10% missing returns, kept 453 clean return days, computed the 99×99 pairwise Pearson correlation matrix, and applied Ward hierarchical clustering.

---

## Asset Frequency (top 20)

Portfolio is valid for **424 of 484 days** (warmup: D001–D060). Total unique assets ever selected: **556** out of 2,270.

| Rank | Asset ID | Count (days) | % Days Selected |
|------|----------|-------------|-----------------|
| 1 | A001224 | 424 | 100.0% |
| 2 | A001347 | 416 | 98.1% |
| 3 | A000151 | 389 | 91.7% |
| 4 | A000989 | 388 | 91.5% |
| 5 | A000466 | 364 | 85.8% |
| 6 | A002187 | 363 | 85.6% |
| 7 | A001369 | 351 | 82.8% |
| 8 | A000474 | 350 | 82.5% |
| 9 | A000744 | 349 | 82.3% |
| 10 | A001546 | 347 | 81.8% |
| 11 | A000928 | 343 | 80.9% |
| 12 | A000200 | 340 | 80.2% |
| 13 | A000651 | 332 | 78.3% |
| 14 | A000773 | 332 | 78.3% |
| 15 | A000987 | 319 | 75.2% |
| 16 | A001142 | 317 | 74.8% |
| 17 | A000475 | 316 | 74.5% |
| 18 | A001402 | 315 | 74.3% |
| 19 | A002261 | 313 | 73.8% |
| 20 | A001834 | 304 | 71.7% |

---

## Portfolio Stability

- **Core holdings (>80% of valid days): 12 stocks** — these are the ultra-stable backbone of the portfolio; A001224 appears every single valid day.
- **Rotating holdings (<80% of days): 544 stocks** — these cycle in and out as relative volatility ranks shift.
- **Never-selected assets: 1,714** — 75% of the universe is permanently excluded (too volatile or illiquid).
- **Average daily turnover: 4.3%** (median 4.0%, max 19.0%, min 0.0%)

At 4.3% daily turnover, approximately 4–5 stocks swap in/out each day on average, incurring low transaction costs — consistent with the backtest finding of ~0.3% total cost drag over the full period.

---

## Return Correlation Clusters

Computed on top-99 most-frequent assets, 453 clean return days (full 484-day span).

**Overall pairwise correlation statistics:**
- Mean: 0.333, Median: 0.336
- 10th percentile: 0.139, 90th percentile: 0.518

**Effective number of independent bets:** ~7.1 (Herfindahl measure on eigenvalue distribution)

**PCA eigenvalue concentration:**
- Largest PC explains 35.4% of return variance
- Top 3 PCs explain 49.2%
- Top 5 PCs explain 54.1%

This is the key risk finding: 100 positions, but ~7 effective independent bets.

### Ward hierarchical clustering (k=5)

| Cluster | Size | Within-cluster mean r | Within-cluster median r |
|---------|----|----------------------|------------------------|
| 1 | 48 | 0.420 | 0.423 |
| 2 | 21 | 0.411 | 0.394 |
| 3 | 16 | 0.554 | 0.558 |
| 4 | 4 | 0.515 | 0.533 |
| 5 | 10 | 0.536 | 0.549 |

**Between-cluster mean correlation: 0.288** (median: 0.289)

The within/between ratio is approximately 1.5×. Clusters 3, 4, and 5 are more tightly coupled (r ≈ 0.52–0.55). Cluster 1 is the largest group (48 assets) with moderate internal correlation (~0.42), likely corresponding to large-cap defensive names (SOEs, banks, utilities). The correlation structure is relatively flat — between-cluster correlation (0.29) is not dramatically lower than within-cluster (0.43), indicating the portfolio is correlated as a whole.

### k=3 clustering (broader grouping)

| Cluster | Size | Within mean r | Between mean r |
|---------|------|--------------|---------------|
| 1 | 48 | — | — |
| 2 | 21 | — | — |
| 3 | 30 | — | — |
| **All** | **99** | **0.419** | **0.284** |

---

## Conclusion

**Risk assessment:** The low_vol portfolio carries significant systemic concentration risk despite holding 100 stocks. The effective number of independent bets is only ~7.1, and the first principal component alone accounts for 35% of return variance. This means the portfolio behaves more like 7 concentrated positions than 100 diversified ones.

The 12 core stocks (permanently held >80% of days) are the primary source of alpha — and the primary source of correlated drawdown risk. Since all 99 analysed assets have a mean pairwise correlation of 0.33, a broad market shock hitting the defensive/low-vol universe (e.g., a rotation from defensives to growth, or a rate shock hitting bond-proxy sectors such as utilities and financials) would likely hit the entire portfolio simultaneously.

**Practical implications for the competition:**
- The MDD of 13.28% observed in-sample is plausible but could worsen if the OOS period (D485–D726) is a recovery/bull rally, which historically punishes low-vol portfolios relative to market.
- The 7 effective bets are positively correlated (between-cluster r = 0.29), so there is no natural hedge within the portfolio.
- No sector neutralisation is possible without sector labels; the portfolio likely overweights bond-proxy sectors (utilities, banks, SOEs) — consistent with the signal's known behaviour in Chinese A-share markets.
- Diversification improvement would require blending with an orthogonal signal (e.g., `lob_imbalance`, which had execution IC = +0.012 and is negatively correlated with daily signals r = −0.24 to −0.57). This would not help concentration directly but would add a return source with different timing.

**Bottom line:** Low turnover (4.3%/day) keeps costs low, which is the main reason the strategy outperforms. The concentration risk is real but has been tolerable in a bear market where low-vol stocks hold value. It remains the primary vulnerability if the OOS regime shifts.
