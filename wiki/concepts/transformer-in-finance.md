# Transformer Architectures in Finance

The transformer's **attention mechanism** enables cross-entity information sharing — the same property that made LLMs work. In finance, the "entities" are assets, and information sharing is cross-asset.

---

## Core Attention Mechanism

```
Attention(Q, K, V) = softmax(QK' / √d_k) V
```

In standard NLP:
- Q = query (current word)
- K = key (all words)
- V = value (all words)
- Output = weighted average of V, with weights proportional to Q-K similarity

**In asset pricing (AIPM paper):**
- Assets are "words"
- Characteristics `X_t` play the role of embeddings
- Attention weight `A_{ij}` between assets i and j = similarity of their characteristics
- Output for asset i = weighted average of all assets' characteristics, weighted by similarity

---

## Two Finance Applications of Attention

### 1. Cross-Asset Pricing (AIPM — [[ai-asset-pricing-models]])
**Goal:** Estimate the SDF / max-SR portfolio  
**Attention over:** Assets, conditioning on their characteristics  
**What it captures:** Expected return of asset i depends on expected returns of similar assets (cross-sectional shrinkage)  
**Architecture:** `A_t = X_t W X'_t`, full transformer blocks stacked in SDF  

### 2. Statistical Arbitrage Factors (Attention Factors — [[attention-factors-stat-arb]])
**Goal:** Construct low-cost, tradable factors optimised for residual trading  
**Attention over:** Firm characteristics to compute factor loadings and portfolio weights  
**What it captures:** Which assets co-move for the purpose of arbitrage (not maximum variance)  
**Architecture:** Attention on embeddings of `X_t` to compute `ω^F_{t-1}` and `β_{t-1}`  

---

## Performance Comparison

| Architecture | OOS Sharpe | Context |
|-------------|-----------|---------|
| Linear SDF (no attention) | 3.6 | Baseline, monthly US |
| Linear portfolio transformer | 3.9 | +attention, same data |
| Nonlinear transformer (10-block) | 4.6 | Full AIPM |
| PCA + transformer residuals (two-step) | ~2.0 net | Stat-arb |
| Attention Factors (one-step) | 2.3 net | Stat-arb |

All Sharpe ratios are out-of-sample. The stat-arb numbers are net of transaction costs; asset pricing numbers are gross.

---

## Why Attention > Standard ML for Finance

1. **Cross-asset information**: stock i's return is predictable from stock j's characteristics if they're similar — attention captures this, MLP doesn't
2. **Variable universe size**: transformers handle `N_t` assets varying over time naturally; fixed-input MLPs cannot
3. **Interpretability**: attention weights `A_{ij}` show which assets are "attending" to each other — often correspond to industry groupings
4. **No handcrafted features needed**: attention learns which characteristics are informative for cross-asset prediction end-to-end

---

## Architecture Notes for Implementation

**Linear Portfolio Transformer** (simplest, closed-form):
```python
# w_t = (X_t W X'_t) X_t λ
A_t = X_t @ W @ X_t.T       # (N x N) attention matrix
w_t = A_t @ X_t @ lambda_    # (N,) portfolio weights

# Equivalent to:
# w_t = X_tilde_t @ lambda_tilde
# where X_tilde has D^3 cross-asset interaction features
```

**Full Nonlinear Transformer** (standard implementation):
```python
import torch.nn as nn
# Standard multi-head attention with softmax, FFN, residual connections
# Each "token" is an asset with characteristic vector as embedding
# Stack K blocks for virtue of complexity
```

---

## Feishu Competition Notes

**Challenge:** The Feishu dataset has no firm characteristics (no book-to-market, no earnings, etc.) — only price, volume, and LOB data. This limits direct use of AIPM-style transformers.

**Workaround:** Use price-based features as pseudo-characteristics:
```python
# Construct "characteristic" vector per asset per day
features = {
    'momentum_5d': ...    # 5-day return
    'momentum_20d': ...   # 20-day return  
    'volatility_20d': ... # 20-day realised vol
    'lob_imbalance': ...  # end-of-day LOB imbalance
    'amihud_illiquidity': ... # |return| / volume
    'price_to_vwap': ...  # close / vwap_0930_0935
}
```
Then the linear portfolio transformer is applicable with these as `X_t`.

**Computationally practical:** The linear portfolio transformer has a closed-form solution. With 2270 assets and ~10 features, this is feasible.

---

## Papers in This Wiki
- [[ai-asset-pricing-models]] — AIPM, linear and nonlinear portfolio transformer
- [[attention-factors-stat-arb]] — attention for factor model + stat-arb
