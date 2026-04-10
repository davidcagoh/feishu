# Factor Models for Chinese A-Shares (Hanauer, Jansen, Swinkels & Zhou, 2024)

**Source:** *International Review of Financial Analysis*, Vol. 91, Article 102975 (January 2024). DOI: 10.1016/j.irfa.2023.102975. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3918833
**Keywords:** asset pricing, factor models, Chinese A-shares, transaction costs, earnings-based value

## Summary

Systematic benchmark of all major factor models (FF3/5/6, q-factor, China-specific variants) on Chinese A-shares 2000–2019 using 105 anomaly portfolios and GRS/HJ-distance tests. Among U.S. models, q-factor wins; China-tailored models win overall. After transaction costs, the model collapses to three factors: **market + size + earnings-based value (E/P)**. Profitability (RMW) and investment (CMA) do not survive realistic trading frictions in this market.

## Key Results

- q-factor best among imported models, beaten by China-tailored four-factor model
- Unconstrained data-driven approach selects seven factors; costs collapse this to three
- Both direct comparison and data-driven methods agree: MKT + SMB + EP
- **Earnings-based value (E/P)** is the dominant value signal; B/M performs poorly in China
- Profitability and investment factors lose significance after transaction costs
- Public factor data released: DOI 10.25397/eur.18817850

## Key Insight for Signal Design

> After costs, three factors survive: market, size, and **E/P**. The rest (profitability, investment, momentum, B/M) are either noise or eaten by trading costs in the A-share context.

This means: focus on **value via earnings yield** and **size** for any fundamental-based signal. Price-based reversal proxies for value (which we already use) are aligned with this finding.

## Implementable Signal

Fundamental E/P data is not in the competition dataset. Best feasible proxies:

**E/P proxy (medium-horizon reversal):**
- In Chinese literature, medium-horizon price reversal loads heavily on earnings value
- `ep_proxy = (adj_close_{t-21} / adj_close_{t-252}) - 1` (12-month return, skip last month)
- Long high EP proxy (undervalued), short low EP proxy

**Size factor:**
- `size_proxy = close * volume` (value-traded as market-cap proxy) per `trade_day_id`
- Long small-size, short large-size (SMB direction)

**Three-factor alpha:**
1. Regress each stock's excess return on market (cross-sectional mean), SMB-proxy spread, EP-proxy spread
2. Alpha residual = stock-specific return unexplained by these factors
3. Use alpha residual as signal target for other predictors (cf. PCA residual analysis)

## Relevance to Feishu Competition

Moderate — direct E/P fundamentals unavailable, but key lesson is directly applicable: **the factor structure that survives in Chinese A-shares is simpler than in the US**. Use size + value-proxy (medium-horizon reversal) as the baseline. Other signals should be evaluated against this three-factor alpha, not raw returns. The PCA residual analysis (see `wiki/results/pca_residual.md`) is consistent with this — daily signals are pure idiosyncratic alpha.

## Status

`[ ] untested` — medium-horizon reversal proxy not yet implemented as separate signal
