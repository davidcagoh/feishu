# Artificial Intelligence Asset Pricing Models (AIPM)

**Authors:** Bryan Kelly, Boris Kuznetsov, Semyon Malamud, Teng Andrea Xu  
**Affiliations:** Yale SOM / AQR / Swiss Finance Institute / EPFL  
**Version:** December 2024  
**SSRN:** 5089371  
**File:** `strategy_papers/ssrn-5089371.pdf`

---

## Core Claim

The fundamental limitation of existing financial ML models is **own-asset prediction**: each stock's portfolio weight depends only on that stock's own characteristics. This is analogous to a bag-of-words language model. Transformers fix this via **cross-asset information sharing** (attention), the same mechanism that made LLMs work. An AIPM implants a transformer in the **Stochastic Discount Factor (SDF)** and achieves state-of-the-art out-of-sample Sharpe ratios.

---

## The Stochastic Discount Factor Framework

The SDF `M_{t+1}` prices assets. In the max-SR portfolio representation:
```
M_{t+1} = 1 - w(X_t)' R_{t+1}
```
where `w(X_t)` is the portfolio weight vector (optimal mean-variance portfolio) and `R_{t+1}` are excess returns.

The goal is to learn `w(X_t)` as a function of characteristics `X_t`.

---

## Model Hierarchy

### Baseline: Own-Asset Prediction (no cross-asset sharing)
```
w_{i,t} = X'_{i,t} λ      (Brandt et al. 2009 — linear)
w_{i,t} = f(X_{i,t}) λ    (DKKM — nonlinear, high-complexity neural net)
```
Sharpe ratios: ~3.6–3.9

### Linear Portfolio Transformer
```
w_t = A_t X_t λ = (X_t W X'_t) X_t λ
```
- `A_t = X_t W X'_t` is the **attention matrix** — similarity between assets based on their characteristics
- `W` (D×D) and `λ` (D×1) are learned parameters
- Information from asset j flows to asset i proportionally to the similarity of their characteristics

**Analytical properties:**
- Equivalent to a linear model with D³ interaction features: `w_t = X̃_t λ̃` where `X̃_t` encodes all pairwise characteristic interactions
- Interpretable as sophisticated **factor timing**: `w'_t R_{t+1} = F'_{t+1} λ_t` where `λ_t` is time-varying factor exposure

**Sharpe: 3.9** (vs 3.6 baseline, same data/architecture but with attention)

### Nonlinear Portfolio Transformer (full AIPM)
Full transformer architecture in the SDF:
- Multi-headed attention
- Softmax transformations
- Feed-forward network (FFN) layers
- Residual connections
- **Multiple stacked transformer blocks** (depth scaling)

**Sharpe by # blocks:**
| Blocks | Parameters | OOS Sharpe |
|--------|-----------|-----------|
| 1 | ~100K | 3.8 |
| 5 | ~500K | 4.3 |
| 10 | ~1M | **4.6** |

Sharpe still increasing at 10 blocks — suggests further gains from scaling.

---

## Key Empirical Results

| Model | OOS Sharpe |
|-------|-----------|
| Linear SDF (no attention) | 3.6 |
| DKKM (nonlinear, no attention) | 3.9 |
| Linear Portfolio Transformer | 3.9 |
| Nonlinear Transformer (1-block) | 3.8 |
| Nonlinear Transformer (10-block) | **4.6** |

**Data:** Monthly US stock returns, 132 characteristics from Jensen et al. (2023), standard anomaly portfolio evaluation.

**Virtue of complexity confirmed:** OOS Sharpe is monotonically increasing in model parameters.

---

## Why Cross-Asset Attention Helps

**Intuition:** If stock i's book-to-market ratio is a noisy signal of expected return, and expected returns are correlated across similar stocks, then using the book-to-market ratios of similar stocks (via attention) gives a less noisy estimate. Attention is cross-sectional Bayesian shrinkage.

More formally: the attention matrix `A_{i,j,t}` reweights stock i's characteristics using a weighted average of all stocks' characteristics, where weights depend on characteristic similarity. This is cross-sectional information sharing.

---

## Relationship to Attention Factors Paper (2510.11616)

Both papers use attention in equity factor models, but with different objectives:
- **AIPM** (this paper): SDF / asset pricing — model risk premia, explain cross-section of expected returns
- **Attention Factors** (2510.11616): Statistical arbitrage — model and trade **residuals** not explained by systematic factors

They are **complementary**: AIPM explains the systematic component (`β' F_t`), while Attention Factors exploit the idiosyncratic component (`ε_{i,t}`). In principle you could chain them.

---

## Relevance to Feishu Competition

| Feishu data | AIPM analog |
|-------------|-------------|
| No firm characteristics available | Major limitation — AIPM requires 132 characteristics |
| Cross-sectional daily returns | The `R_{t+1}` that `w_t` is trying to predict |
| 2270 assets × 484 days | Smaller but similar panel structure |

**Direct applicability is limited** because the Feishu dataset has no fundamental characteristics (only price/volume/LOB). However:
- The **cross-asset information sharing** insight is transferable: instead of firm characteristics, use price-based features (momentum, volatility, LOB imbalance) as `X_t`, then run attention across assets
- The **factor timing** interpretation suggests: build factor portfolios from price-based signals, then dynamically reweight using cross-sectional information
- The **linear portfolio transformer** architecture is simple enough to implement from scratch

---

## Concepts
→ [[stochastic-discount-factor]] | [[factor-models]] | [[transformer-in-finance]] | [[statistical-arbitrage]]
