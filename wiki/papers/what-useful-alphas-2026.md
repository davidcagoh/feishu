# What Useful Alphas?

**Authors:** Andrew Y. Chen, Ivo Welch  
**Venue/Source:** arXiv (targeted for Financial Analysts Journal)  
**arXiv/DOI:** arXiv:2607.06502  
**Date:** July 8, 2026

---

## Core Claim
Approximately 200 published long-short anomaly equity portfolios have delivered essentially zero alpha to non-micro-cap portfolio managers in the post-2005 era: after filtering for post-publication years and large/mid-cap stocks, the median zero-investment return is only 7 bp/month — a figure that disappears under any realistic transaction cost or luck adjustment.

---

## Method
Examines the Chen-Zimmermann (2022) database of ~200 published long-short anomaly portfolios (size, value, momentum, profitability, investment, etc.). Partitions the sample along two dimensions:
- **Time**: pre-2005 (when anomalies were discovered) vs. post-2005 (after publication)
- **Stock universe**: all-stock (micro-cap inclusive) vs. non-micro (top 3,000 by market cap = top 90% of market cap)

Median zero-investment return by partition:
| Period | Universe | Median return |
|--------|----------|--------------|
| ≤ 2005 | All stocks | 48 bp/month |
| > 2005 | All stocks | 19 bp/month |
| ≤ 2005 | Non-micro | 26 bp/month |
| > 2005 | Non-micro | **7 bp/month** |

The 7 bp/month figure is the investment-relevant number: post-publication, large/mid-cap stocks only. Even modest transaction costs or luck adjustment eliminates this.

---

## Results
**Conclusion:** Public stock markets were essentially efficient for non-micro-cap portfolio managers since 2006. Published academic anomalies have been useless to any manager who cannot invest in micro-caps. The paper targets Financial Analysts Journal (practitioner-focused).

Key asymmetry: the 48→7 bp decay is driven equally by (1) the post-publication effect (arbitrage-in) and (2) the micro-cap exclusion. Both factors are necessary to reach the full ~85% decay. Small stocks exhibit anomalies that are persistent but not exploitable by institutional-scale mandates.

---

## Implementable Idea
None — meta-analytic result, not a new signal. The implementable implication is a **negative constraint**: do not add published anomaly factor screens to a minimum-variance portfolio selection unless there is specific structural (non-arbitrage) reason for the factor to persist in the operating universe (e.g., Chinese A-share microstructure constraints that prevent institutional arbitrage).

The one exception: structural signals grounded in *specific, exploitable market frictions* (T+1 settlement, ±10% price limits, retail crowding under daily vol limits) are more likely to survive because the friction itself limits arbitrage. This class includes our trend filter and vol ranking, not generic published anomaly factors.

**Addresses priority:** Priority 3 (Stock selection within the low-vol universe) — closes the question of whether adding generic published anomaly factors (size, value, momentum, profitability) to our N=20 low-vol screen is worth pursuing. The answer is: no.

---

## Relevance to Feishu Competition
This paper validates the meta-strategy of the Feishu project:
1. **Validates anti-anomaly stance**: Our IC-era signals (volume_reversal, alpha191_046, alpha191_071, short_term_reversal) failed in portfolio construction. This paper provides a second, independent reason beyond the execution gap: even if the execution gap were eliminated, published anomaly factors don't work in large/mid-cap stocks post-2005.
2. **Validates Signals #24–#36 selection logic**: The signals we added post-IC are all motivated by *structural* Chinese market frictions (T+1, ±10% limits, retail crowding, overnight-return MAX), NOT by generic published anomaly scores. The Chen-Welch result doesn't apply to structurally-motivated signals.
3. **Closes an open investigation path**: Future sessions should not explore adding generic published factor screens (value, quality, earnings growth, etc.) to the low-vol universe, even with Chinese A-share data. The Li et al. (Management Science, 2024) Chinese-specific evidence is consistent: 83.37% of Chinese anomaly variables generate no significant return.
4. **Sharpens Priority 3**: The remaining valid approach for Priority 3 is structural screens (limit-move masking, turnover filter, overnight MAX filter) — not new published anomalies.

---

## Concepts
-> [[factor-models]] | [[chinese-ashore-market]] | [[statistical-arbitrage]]
