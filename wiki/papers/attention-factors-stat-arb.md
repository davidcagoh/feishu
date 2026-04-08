# Attention Factors for Statistical Arbitrage

**Authors:** Elliot L. Epstein, Rose Wang, Jaewon Choi, Markus Pelger (Stanford / Hanwha Life)  
**Venue:** ICAIF '25 (ACM Int'l Conference on AI in Finance, Nov 2025, Singapore)  
**arXiv:** 2510.11616v1  
**File:** `strategy_papers/2510.11616v1.pdf`

---

## Core Claim

Standard stat-arb is a **two-step pipeline**: (1) estimate factors to explain cross-sectional variation, then (2) extract mispricing signals from residuals. These two steps are decoupled, so the factors aren't optimised for trading — they have high turnover and large short positions that destroy net performance. This paper proposes a **one-step joint solution** that simultaneously learns factors and trading policy, optimising directly for net Sharpe ratio after transaction costs.

---

## Method

### The Three-Problem Decomposition of Stat-Arb
1. **Identify similar assets** — construct arbitrage portfolios (mimicking portfolios that hedge systematic risk)
2. **Extract mispricing signals** — find time-series signals in factor residuals
3. **Form a trading policy** — allocate to maximise risk-adjusted returns after costs

### Conditional Factor Model
Assets returns decomposed as:

```
R_{i,t} = β_{i,t-1}^T F_t + ε_{i,t}
```

Where `F_t` are K tradable factors, `β` are time-varying loadings, and `ε_{i,t}` is the "mispricing" residual the strategy trades.

### Attention Factors
The key innovation: factor portfolio weights are computed via an **attention mechanism** over firm characteristic embeddings:

```
F_t = ω^F_{t-1} R_t        (tradable factor portfolio)
ω^F_{t-1} = softmax(X_t Q_k) × X_t   (attention over characteristics)
```

- `X_t ∈ R^{N×M}` — N assets × M firm characteristics
- K query vectors `Q_k` — one per factor
- Loadings `β` are also computed via attention (inner products between embeddings)

This is a **conditional** factor model where loadings and factors are both functions of firm characteristics, learned end-to-end.

### Sequence Model for Residual Trading
Lagged residual portfolios `{ε_{t-1}, ε_{t-2}, ...}` are fed into a **Long Convolution (LongConv)** sequence model to produce portfolio weights in the residual space. These are then mapped back to asset space via the composition matrix.

### Joint Training Objective
```
maximise:  net Sharpe ratio  -  turnover penalty
```
Both the attention factor module and the sequence model are trained jointly. This is the critical difference from prior work — factors can adapt to reduce trading costs.

---

## Prior SOTA Context
The benchmark they beat is [19] = some transformer-on-PCA-residuals paper (two-step approach). Their one-step method achieves **84% higher net Sharpe** than this benchmark.

---

## Results
| Metric | Value |
|--------|-------|
| OOS Sharpe (gross) | > 4.0 |
| OOS Sharpe (net of transaction costs) | **2.3** |
| Annual return | ~16% |
| Market correlation | ~0 |
| Universe | 500 largest US equities |
| Period | 24 years (daily returns) |
| Characteristics used | Extensive set of firm characteristics |

**Key finding:** Weak factors (low explained variance) are disproportionately important for arbitrage trading. Standard PCA misses these because it optimises for explained variance, not profitability.

---

## Relevance to Feishu Competition

| Feishu data | Paper analog |
|-------------|--------------|
| `asset_id` characteristics | Firm characteristics `X_t` |
| Cross-sectional daily returns | Factor model `R_{i,t}` |
| LOB snapshot signals | Could serve as conditioning variables |
| 484 trading days × 2270 assets | Smaller universe, similar structure |

**Implementable ideas:**
- Use cross-sectional standardised return residuals after removing a few PCA factors as the "mispricing" signal
- Even without the full attention architecture, the insight about joint optimisation can inform alpha construction: build signals that are explicitly low-turnover
- The "weak factors" finding suggests not over-regularising: signals with low IC but low correlation to others may still add value in combination

---

## Concepts
→ [[statistical-arbitrage]] | [[factor-models]] | [[transformer-in-finance]] | [[mean-reversion]]
