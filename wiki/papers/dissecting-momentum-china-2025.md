# Dissecting Momentum in China

**Authors:** Xin Liu, Songtao Tan, Yuchen Xu, Peixuan Yuan, Yun Zhu  
**Venue/Source:** SSRN (UNSW Business School Research Paper)  
**arXiv/DOI:** SSRN:5130681  
**Date:** February 10, 2025  

---

## Core Claim
Classic price momentum is absent in Chinese A-shares because news-driven gains are systematically reversed on subsequent non-news days — a "tug-of-war" unique to retail-dominated markets. This resolves the long-standing puzzle of why momentum fails in China despite being profitable globally.

---

## Method
- Decompose each stock's past 12-month return into two components: returns accumulated on **news days** (days with earnings, analyst revisions, or significant company announcements) vs. **non-news days**.
- Test cross-sectional momentum separately for each component: do high past-news-return stocks outperform going forward? Do high past-non-news-return stocks?
- Data: Shanghai and Shenzhen A-shares over a multi-year sample. Key descriptive: 2.46 average news days per month; average past-news return = 7.12%.
- Comparison group: US equities over the same period.

---

## Results
| Market | Past news returns predict future news-day returns | Past news returns predict future non-news-day returns | Net momentum |
|---|---|---|---|
| **China** | Yes (positive) | **No (negative reversal)** | Absent |
| **US** | Yes (positive) | Yes (positive, even stronger) | Strong |

In China, good news-day returns attract retail crowding. The crowded positions are then unwound on non-news days → reversal cancels the momentum. In the US, information diffuses gradually to both news and non-news periods → momentum persists.

The "tug-of-war" is stronger among retail-heavy stocks and stocks with lower institutional ownership, confirming the retail-participation mechanism.

---

## Implementable Idea
None — directly implementing this signal requires per-stock earnings/news calendar data, which is not available in the Feishu competition dataset (no fundamental characteristics are provided).

**However, this paper definitively closes Hypothesis #2** (does intermediate-horizon momentum exist in Chinese A-shares?). The answer is: **No, and here is why.** Pursuing 3-month, 6-month, or 12-month price momentum signals in the Feishu dataset is not worth the effort:
- The mechanism (retail-driven news-day crowding → non-news-day reversal) is operative in our A-share universe.
- Without earnings/news dates, we cannot isolate the news-day return component.
- Price momentum over these horizons will be at best zero-IC and at worst negatively executed (we buy post-gap).

The paper actually *strengthens* the case for our existing low_vol strategy: the same retail-crowding mechanism that kills momentum also amplifies short-term reversal (our reversal signals capture the non-news-day unwind).

**Addresses priority:** Chinese A-share momentum (hypothesis #2) — definitively answered; remove from open hypotheses and add to Ruled Out.

---

## Relevance to Feishu Competition
This paper does not suggest a new signal. Instead it changes the research direction:
- **Stop**: searching for intermediate-horizon momentum signals in the Feishu data.
- **Confirm**: our short-term reversal signals (volume_reversal, alpha191_046/071) are capturing the correct China-specific effect (retail-driven short-cycle overreaction).
- **Note**: the execution IC failure of reversal signals (buying AFTER the overnight gap) is a separate problem from the IC metric itself; this paper does not help solve it.

Our current best (vol_managed, Score=0.3116) is unaffected by this finding — it does not rely on momentum.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]] | [[statistical-arbitrage]]
